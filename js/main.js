function loadpage() {
    restorePersistantState();
};

/*
 * Run SASCALC for the current instrument and model
 */
function SASCALC(instrument, averageType="Circular", model="Debye") {
    // Calculate the beam stop diameter
    calculateBeamStopDiameter(instrument);
    // Calculate the estimated beam flux
    calculateBeamFlux(instrument);
    // Calculate the figure of merit
    calculateFigureOfMerit(instrument);
    // Calculate the number of attenuators
    calculateNumberOfAttenuators(instrument);
    // Do Circular Average of an array of 1s
    calculateQRange(instrument, averageType);
    // Do Circular Average of an array of 1s
    calculateModel(model);
    // Update the chart
    update1DChart();

    // TODO: Populate minimum and maximum Q values
    // TODO: Calculate model in Q range

    // Store persistant state
    storePersistantState(instrument);
}

/*
 * Calculate the q values for a given configuration
 */
function calculateQRange(instrument, averageType="Circular") {
    var xPixels = parseInt(window[instrument + "Constants"]["xPixels"]);
    var yPixels = parseInt(window[instrument + "Constants"]["yPixels"]);
    var xCenter = xPixels / 2 + 0.5;
    var yCenter = calculateYBeamCenter(instrument);
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]);
    var coeff = parseFloat(window[instrument + "Constants"]["coeff"]);
    var xDistance = yDistance = totalDistance = correctedDx = correctedDy = dataPixel = numDSquared = 0;
    var radiusCenter = 100;
    var numDimensions = center = largeNumber = 1;
    var smallNumber = 1e-10;
    var i = j = k = l = nq = 0;

    // Detector values pixel size in mm
    var detectorDistance = parseFloat(document.getElementById(instrument + "SDDInputBox").value) * 10;
    var mask = generateStandardMask(instrument);
    var maskI = new Array();
    var data = generateOnesData(instrument);
    var dataI = new Array();

    // Loop over each pixel
    for (i = 0; i < xPixels; i++) {
        xDistance = calculateDistanceFromBeamCenter(i, xCenter, pixelSize, coeff);
        maskI = mask[i];
        dataI = data[i];
        for (j = 0; j < yPixels; j++) {
            yDistance = calculateDistanceFromBeamCenter(j, yCenter, pixelSize, coeff);
            // Ignore masked pixels (mask[i][j] = 1)
            if (maskI[j] == 0) {
                dataPixel = dataI[j];
                numDSquared = numDimensions * numDimensions;
                totalDistance = Math.sqrt(xDistance * xDistance + yDistance * yDistance);
                // Break pixels up into a 3x3 grid close to the beam center
                if (totalDistance > radiusCenter) {
                    numDimensions = 1;
                    center = 1;
                } else {
                    numDimensions = 3;
                    center = 2;
                }
                // Loop over sliced pixels
                for (k = 1; k <= numDimensions; k++) {
                    correctedDx = xDistance + (k - center) * pixelSize / numDimensions;
                    for (l = 1; l <= numDimensions; l++) {
                        correctedDy = yDistance + (l - center) * pixelSize / numDimensions;
                        switch (averageType) {
                            case "Circular":
                            default:
                                var iRadius = Math.floor(Math.sqrt(correctedDx * correctedDx + correctedDy * correctedDy) / pixelSize) + 1;
                                break;
                            // TODO: Add in other averaging types
                        }
                        nq = (iRadius > nq) ? iRadius : nq;
                    }
                }
            }
        }
    }

    // Define data for display
    window.qValues = new Array(nq).fill(0);
    window.aveIntensity = new Array(nq).fill(0);
    window.nCells = new Array(nq).fill(0);
    window.dSQ = new Array(nq).fill(0);
    window.sigmaAve = new Array(nq).fill(0);
    window.qAverage = new Array(nq).fill(0);
    window.sigmaQ = new Array(nq).fill(0);
    window.fSubs = new Array(nq).fill(0);

    // TODO: Find a way to simplify rather than looping over the same items twice
    // Loop over each pixel
    for (i = 0; i < xPixels; i++) {
        xDistance = calculateDistanceFromBeamCenter(i, xCenter, pixelSize, coeff);
        maskI = mask[i];
        dataI = data[i];
        for (j = 0; j < yPixels; j++) {
            yDistance = calculateDistanceFromBeamCenter(j, yCenter, pixelSize, coeff);
            // Ignore masked pixels (mask[i][j] = 1)
            if (maskI[j] == 0) {
                dataPixel = dataI[j];
                numDSquared = numDimensions * numDimensions;
                totalDistance = Math.sqrt(xDistance * xDistance + yDistance * yDistance);
                // Break pixels up into a 3x3 grid close to the beam center
                if (totalDistance > radiusCenter) {
                    numDimensions = 1;
                    center = 1;
                } else {
                    numDimensions = 3;
                    center = 2;
                }
                // Loop over sliced pixels
                for (k = 1; k <= numDimensions; k++) {
                    correctedDx = xDistance + (k - center) * pixelSize / numDimensions;
                    for (l = 1; l <= numDimensions; l++) {
                        correctedDy = yDistance + (l - center) * pixelSize / numDimensions;
                        switch (averageType) {
                            case "Circular":
                            default:
                                var iRadius = Math.floor(Math.sqrt(correctedDx * correctedDx + correctedDy * correctedDy) / pixelSize) + 1;
                                break;
                            // TODO: Add in other averaging types
                        }
                        calculateIntensityValues(iRadius, dataPixel, numDSquared);
                    }
                }
            }
        }
    }

    var lambda = parseFloat(document.getElementById(instrument + "WavelengthInput").value);
    var ntotal = theta = radius = aveSQ = aveisq = diff = 0;
    // Loop over every q value
    for (i = 0; i <= nq; i++) {
        radius = (2 * i) * pixelSize / 2;
        theta = Math.atan(radius / detectorDistance) / 2;
        window.qValues[i] = (4 * Math.PI / lambda) * Math.sin(theta);
        if (window.nCells[i] <= 1) {
            window.aveIntensity[i] = (window.nCells[i] == 0) ? 0 : window.aveIntensity[i] / window.nCells[i];
            window.sigmaAve[i] = largeNumber;
        } else {
            window.aveIntensity[i] = window.aveIntensity[i] / window.nCells[i];
            aveSQ = window.aveIntensity[i] * window.aveIntensity[i];
            aveisq = window.dSQ[i] / window.nCells[i];
            diff = aveisq - aveSQ;
            window.sigmaAve[i] = (diff < 0) ? largeNumber : Math.sqrt(diff / (window.nCells[i] - 1));
        }
        calculateResolutions(i, instrument);
        ntotal += window.nCells[i];
    }
}

/*
 * Calculate the model function used to represent the data
 */
function calculateModel(model="Debye") {
    // TODO: Tie into sasmodels
    var defaultParams = Object.values(window.modelList[model]['params']);
    window[model.toLowerCase()](defaultParams);
    for (var i = 0; i < window.aveIntensity.length; i++) {
        window.aveIntensity[i] *= window.fSubs[i];
    }
}

/*
 * Calculate the number of q points, and sum the intensities, dsq, and number of cells.
 */
function calculateIntensityValues(iRadius, dataPixel, numDSquared) {
    window.aveIntensity[iRadius - 1] += dataPixel / numDSquared;
    window.dSQ[iRadius - 1] += dataPixel * dataPixel / numDSquared;
    window.nCells[iRadius - 1] += 1 / numDSquared;
}

/*
 * Calculate the beam center in pixels
 */
function calculateYBeamCenter(instrument) {
    // Find the number of y pixels in the detector
    var yPixels = parseInt(window[instrument + "Constants"]["yPixels"]);
    // Get pixel size in mm and convert to cm
    var dr = parseFloat(window[instrument + "Constants"]["aPixel"]) / 10;
    // Get detector offset in cm
    var offset = parseFloat(document.getElementById(instrument + "OffsetInputBox").value);
    var yCenter = (offset / dr) + (yPixels / 2 + 0.5);
    return yCenter;
}

/*
 * Calculate the x or y distance from the beam center of a given pixel
 */
function calculateDistanceFromBeamCenter(pixelValue, pixelCenter, pixelSize, coeff) {
    return coeff * Math.tan((pixelValue - pixelCenter) * pixelSize / coeff);
}

/*
 * Calculate the resolutions for the ith q value
 */
function calculateResolutions(i, instrument) {
    var lambda = parseFloat(document.getElementById(instrument + "WavelengthInput").value);
    var lambdaWidth = parseFloat(document.getElementById(instrument + "WavelengthSpread").value);
    var isLenses = Boolean(document.getElementById(instrument + "GuideConfig") === "LENS");
    // Get values and be sure they are in cm
    var sourceApertureRadius = parseFloat(document.getElementById(instrument + "SourceAperture").value) * 0.5 * 0.1;
    var sampleApertureRadius = parseFloat(document.getElementById(instrument + "SampleAperture").value) * 0.5 * 0.1;
    var apertureOffset = parseFloat(window[instrument + "Constants"]["ApertureOffset"]);
    var beamStopSize = calculateBeamStopDiameter(instrument) * 2.54;
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]) * 0.1;
    // SSD and SDD in cm, corrected for the aperture offset
    var SSD = calculateSourceToSampleApertureDistance(instrument);
    var SDD = calculateSampleToDetectorDistance(instrument) + apertureOffset;
    var qValue = window.qValues[i];
    // Define constants
    var velocityNeutron1A = 3.956e5;
    var gravityConstant = 981.0;
    // Base calculations
    var a2 = sourceApertureRadius * SDD / SSD + sampleApertureRadius * (SDD + SSD) / SSD;
    var q_small = 2 * Math.PI * (beamStopSize - sampleApertureRadius) * (1 - lambdaWidth) / (lambda * SDD);
    document.getElementById(instrument + "MinimumQ").value = Math.round(q_small, 1000000) / 1000000;
    var lp = 1 / (1 / SDD + 1 / SSD);
    // Calculate variances
    var varLambda = lambdaWidth * lambdaWidth / 6.0;
    if (isLenses) {
        var varBeam = 0.25 * Math.pow(sourceApertureRadius * SDD / SSD, 2) + 0.25 * (2 / 3) * Math.pow(lambdaWidth / lambda, 2) * Math.pow(sampleApertureRadius * SDD / lp, 2);
    } else {
        var varBeam = 0.25 * (sourceApertureRadius * SDD / SSD) * (sourceApertureRadius * SDD / SSD) + 0.25 * (sampleApertureRadius * SDD / lp) * (sampleApertureRadius * SDD / lp);
    }
    var varDetector = Math.pow(pixelSize / 2.3548, 2) + (pixelSize * pixelSize) / 12;
    var velocityNeutron = velocityNeutron1A / lambda;
    var varGravity = 0.5 * gravityConstant * SDD * (SSD + SDD) / Math.pow(velocityNeutron, 2);
    var rZero = SDD * Math.tan(2.0 * Math.asin(lambda * qValue / (4.0 * Math.PI)));
    var delta = 0.5 * Math.pow(beamStopSize - rZero, 2) / varDetector;

    // TODO: Find usable incomplete gamma function in javascript (or php)
    var incGamma = 1.00e-10;
    //if (rZero < beamStopSize) {
    //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 - gammainc(1.5, delta) / math.gamma(1.5));
    //} else {
    //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 + window.gammainc(1.5, delta) / math.gamma(1.5));
    //}
    var fSubS = 0.5 * (1.0 + math.erf((rZero - beamStopSize) / Math.sqrt(2.0 * varDetector)));
    if (fSubS <= 0.0) {
        fSubS = 1e-10;
    }
    var fr = 1.0 + Math.sqrt(varDetector) * Math.exp(-1.0 * delta) / (rZero * fSubS * math.sqrt(2.0 * Math.PI));
    var fv = incGamma / (fSubS * Math.sqrt(Math.PI)) - rZero * rZero * Math.pow(fr - 1.0, 2) / varDetector;
    var rmd = fr + rZero;
    var varR1 = varBeam + varDetector * fv + varGravity;
    var rm = rmd + 0.5 * varR1 / rmd;
    var varR = varR1 - 0.5 * (varR1 / rmd) * (varR1 / rmd);
    if (varR < 0) {
        varR = 0.0;
    }
    window.qAverage[i] = (4.0 * Math.Pi / lambda) * Math.sin(0.5 * Math.atan(rm / SDD));
    window.sigmaQ[i] = window.qAverage[i] * Math.sqrt((varR / rmd) * (varR / rmd) + varLambda);
    window.fSubs[i] = fSubS;
}

/*
 * Generate a standard SANS mask with the outer 2 pixels masked
 */
function generateStandardMask(instrument) {
    var xPixels = parseInt(window[instrument + "Constants"]["xPixels"]);
    var yPixels = parseInt(window[instrument + "Constants"]["yPixels"]);
    var mask = new Array();
    for (var i = 0; i < xPixels; i++) {
        var maskInset = new Array();
        for (var j = 0; j < yPixels; j++) {
            if (i <= 1 || i >= xPixels - 2) {
                // Top and bottom two pixels should be masked
                maskInset[j] = 1;
            } else if (j <= 1 || j >= yPixels - 2) {
                // Left and right two pixels should be masked
                maskInset[j] = 1;
            } else {
                // Remainder should not be masked
                maskInset[j] = 0;
            }
        }
        mask[i] = maskInset;
    }
    return mask;
}

/*
 * Generate a data set of all ones for a given detector
 */
function generateOnesData(instrument) {
    var xPixels = parseInt(window[instrument + "Constants"]["xPixels"]);
    var yPixels = parseInt(window[instrument + "Constants"]["yPixels"]);
    var data = new Array();
    var dataY = new Array();
    for (var i = 0; i < xPixels; i++) {
        for (var j = 0; j < yPixels; j++) {
            dataY[j] = 1;
        }
        data[i] = dataY;
    }
    return data;
}

/*
 * Calculate the estimated beam flux
 */
function calculateBeamFlux(instrument) {
    var beamFlux = document.getElementById(instrument + 'BeamFlux');
    // TODO: Run calculation
    beamFlux.value = 1000.0;
    return parseFloat(beamFlux.value);
}

/*
 * Calculate the estimated beam flux
 */
function calculateFigureOfMerit(instrument) {
    var lambda = parseFloat(document.getElementById(instrument + 'WavelengthInput').value);
    var beamFlux = parseFloat(document.getElementById(instrument + 'BeamFlux').value);
    var figureOfMerit = document.getElementById(instrument + 'FigureOfMerit');
    var figureOfMeritValue = lambda * lambda * beamFlux;
    figureOfMerit.value = figureOfMeritValue;
}

/*
 * Calculate the estimated attenuation factor needed to keep the beam intensity lower than the maximum countrate per pixel
 */
function calculateAttenuationFactor(instrument) {
    var attenFactorNode = document.getElementById(instrument + "AttenuationFactor");
    var a2 = getSampleApertureSize(instrument);
    var beamDiam = calculateBeamDiameter(instrument);
    var aPixel = parseFloat(window[instrument + "Constants"]["aPixel"]);
    var iPixelMax = parseFloat(window[instrument + "Constants"]["iPixel"]);
    var num_pixels = Math.PI / 4 * (0.5 * (a2 + beamDiam)) * (0.5 * (a2 + beamDiam)) / aPixel / aPixel;
    var iPixel = calculateBeamFlux(instrument) / num_pixels;
    var atten = (iPixel < iPixelMax) ? 1.0 : iPixelMax / iPixel;
    attenFactorNode.value = Math.round(atten * 100000) / 100000;
    return atten;
}

/*
 * Calculate the number of attenuators needed for transmission measurements
 */
function calculateNumberOfAttenuators(instrument) {
    var atten = calculateAttenuationFactor(instrument);
    var attenuatorNode = document.getElementById(instrument + "Attenuators");
    var wavelength = parseFloat(document.getElementById(instrument + "WavelengthInput").value);

    var af = 0.498 + 0.0792 * wavelength - 1.66e-3 * wavelength * wavelength;
    var nf = -Math.log(atten) / af;
    var numAtten = Math.floor(nf) + 1;
    if (numAtten > 6) {
        numAtten = 7 + Math.floor((numAtten - 6) / 2);
    }
    attenuatorNode.value = numAtten;
}

/*
 * Calculate the beam stop diameter needed to cover the beam
 */
function calculateBeamStopDiameter(instrument) {
    var beamDiamNode = document.getElementById(instrument + "BeamSize");
    var beamStopDiamNode = document.getElementById(instrument + "BeamStopSize");
    var bm = calculateBeamDiameter(instrument, 'maximum');
    beamDiamNode.value = Math.round(bm * 10000) / 10000;
    // TODO: ngb10m has 1.5" BS, but no 2"
    var bsDiam = Math.ceil(bm / 2.54);
    if (document.getElementById(instrument + 'GuideConfig').value === 'LENS') {
        // If LENS configuration, the beam size is the source aperture size
        bsDiam = 1;
    }
    beamStopDiamNode.value = bsDiam;
    return bsDiam;
}

function getSampleApertureSize(instrument) {
    var sampleAperture = document.getElementById(instrument + 'SampleAperture').value;
    if (sampleAperture === 'Custom') {
        return parseFloat(document.getElementById(instrument + 'CustomAperture').value);
    } else {
        // Default values in inches - convert to cm
        return parseFloat(sampleAperture) * 2.54;
    }
}

/*
 * Calculate the beam diameter at the detector
 */
function calculateBeamDiameter(instrument, direction = 'maximum') {
    // Get values for the desired instrument
    var a1 = parseFloat(document.getElementById(instrument + 'SourceAperture').value);
    var l1 = calculateSourceToSampleApertureDistance(instrument);
    var l2 = calculateSampleToDetectorDistance(instrument)
    if (document.getElementById(instrument + 'GuideConfig').value === 'LENS') {
        // If LENS configuration, the beam size is the source aperture size
        return a1;
    }
    var a2 = getSampleApertureSize(instrument);
    var lambda = parseFloat(document.getElementById(instrument + 'WavelengthInput').value);
    var lambdaDelta = parseFloat(document.getElementById(instrument + 'WavelengthSpread').value) / 100.0;
    var bsFactor = parseFloat(window[instrument + 'Constants']['BSFactor']);
    // Calculate beam size on the detector
    var d1 = a1 * l2 / l1;
    var d2 = a2 * (l1 + l2) / l1;
    // Beam width
    var bw = d1 + d2;
    // Beam height due to gravity
    var bv = parseFloat(bw + 1.25e-8 * (l1 + l2) * l2 * lambda * lambda * lambdaDelta);
    // Larger of the width*safetyFactor and height
    var bm_bs = parseFloat(bsFactor * bw);
    let bm = (bm_bs > bv) ? bm_bs : bv;
    switch (direction) {
        case 'vertical':
            return bv;
            break;
        case 'horizontal':
            return bh;
            break;
        case 'maximum':
        default:
            return bm;
    }
}

/*
 *  Calculate the sample to detector distance
 */
function calculateSampleToDetectorDistance(instrument) {
    var sdd = parseFloat(document.getElementById(instrument + 'SDDInputBox').value);
    var sampleSpace = document.getElementById(instrument + 'SampleTable').value;
    var sddOffset = parseFloat(window[instrument + 'Constants'][sampleSpace + 'Offset']);
    var SDD = document.getElementById(instrument + 'SDD');
    var l2 = sdd + sddOffset;
    SDD.value = l2;
    return l2;
}

/*
 *  Calculate the source to sample distance
 */
function calculateSourceToSampleApertureDistance(instrument) {
    // TODO: Separate this out into smaller functions probably
    // Get the number of guides
    var SSD = document.getElementById(instrument + 'SSD');
    var guides = document.getElementById(instrument + 'GuideConfig').value;
    if (guides === "LENS") {
        guides = "0";
    }
    var nGds = parseFloat(guides);
    // Get the sample location
    var sampleSpace = document.getElementById(instrument + 'SampleTable').value;
    var ssd = 0.0;
    var ssdOffset = parseFloat(window[instrument + 'Constants'][sampleSpace + 'Offset']);
    var apertureOffset = parseFloat(window[instrument + 'Constants']['ApertureOffset'])
    // Calculate the source to sample distance
    switch (instrument) {
        case 'ng7':
        case 'ngb30m':
            ssd = 1632 - 155 * nGds - ssdOffset - apertureOffset;
            break;
        case 'ngb10m':
            ssd = 513 - ssdOffset;
            if (nGds != 0) {
                ssd -= 61.9;
                ssd -= 150 * nGds;
            }
            ssd -= apertureOffset;
            break;
        default:
            ssd = 0.0;
    }
    SSD.value = ssd;
    return ssd;
}

/*
 * Use the updated guide values to calculate the Q ranges for the current instrument
 */
function updateGuides(instrument, guideSelectStr, runSASCALC = true) {
    // Get guide nodes for the specific instrument
    var apertureNode = document.getElementById(instrument + "SourceAperture");
    var allApertureOptions = Object.values(apertureNode.options);
    var aperturesName = instrument + "SourceApertures";
    var guideApertureOptions = Object.values(window[aperturesName][guideSelectStr]).join(" ");
    // Show only source apertures allowed for the current guide configuration
    for (aperture in allApertureOptions) {
        var apertureValue = allApertureOptions[aperture].value.toString();
        if (guideApertureOptions.includes(apertureValue)) {
            allApertureOptions[aperture].disabled = false;
            allApertureOptions[aperture].hidden = false;
            allApertureOptions[aperture].selected = true;
            sessionStorage.setItem(instrument + "SourceAperture", allApertureOptions[aperture].value);
        } else {
            allApertureOptions[aperture].disabled = true;
            allApertureOptions[aperture].hidden = true;
        }
    }
    if (runSASCALC) {
        SASCALC(instrument);
    }
};

/*
 * Use the updated detector values to calculate the Q ranges for the current instrument
 */
function updateDetector(instrument, runSASCALC = true) {
    // Get detector nodes for the specific instrument
    var detectorSlider = document.getElementById(instrument + "SDDSliderBar");
    var detectorOutput = document.getElementById(instrument + "SDDInputBox");
    var offsetSlider = document.getElementById(instrument + "OffsetSliderBar");
    var offsetOutput = document.getElementById(instrument + "OffsetInputBox");
    // Set outputs and sliders to the same value
    detectorOutput.value = detectorSlider.value;
    offsetOutput.value = offsetSlider.value;
    // Update the current slider value (each time you drag the slider handle)
    detectorSlider.oninput = function () { detectorOutput.value = this.value; }
    detectorOutput.oninput = function () { detectorSlider.value = this.value; }
    offsetSlider.oninput = function () { offsetOutput.value = this.value; }
    offsetOutput.oninput = function () { offsetSlider.value = this.value; }
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Use the updated aperture values to calculate the Q ranges for the current instrument
 */
function updateAperture(instrument, runSASCALC = true) {
    // Get aperture nodes for the specific instrument
    var customAperture = document.getElementById(instrument + 'CustomAperture');
    var customApertureLabel = document.getElementById(instrument + 'CustomApertureLabel');
    var sampleApertureSelector = document.getElementById(instrument + 'SampleAperture');
    // Show/hide custom aperture size box
    if (sampleApertureSelector.value === "Custom") {
        customAperture.style.display = 'inline-block';
        customApertureLabel.style.display = 'inline-block';
    } else {
        customAperture.style.display = 'none';
        customApertureLabel.style.display = 'none';
    }
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Use the updated wavelength spread to determine the allowed wavelength range
 */
function updateWavelengthSpread(instrument, runSASCALC=true) {
    var wavelength = document.getElementById(instrument + 'WavelengthInput');
    var wavelengthSpread = document.getElementById(instrument + 'WavelengthSpread').value;
    var wavelengthOptions = window[instrument + 'WavelengthRange'][wavelengthSpread];
    wavelength.min = parseFloat(wavelengthOptions[0]);
    wavelength.max = parseFloat(wavelengthOptions[1]);
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Change the instrument you want to calculate Q ranges for
 */
function updateInstrument(domName, selectStr, runSASCALC=true) {
    // Get instrument node and create an array of the options available
    var inst = document.getElementById(domName);
    var instrumentOptions = [];
    for (var i = 0; i < inst.options.length; i++) {
        instrumentOptions.push(inst.options[i].value);
    }
    var instruments = {};
    var instName = "";
    // Get the divs for all possible instruments
    for (var j in instrumentOptions) {
        instName = instrumentOptions[j]
        if (!(instName === "")) {
            instruments[instName] = document.getElementById(instName);
        }
    }
    // Show selected instrument and hide all others
    for (var key in instruments) {
        if (key === selectStr) {
            instruments[key].style.display = "block";
        } else {
            instruments[key].style.display = "none";
        }
    }
    if (runSASCALC) {
        SASCALC(selectStr);
    }
};

/*
 * Update the 1D Chart with new data sets
 */
function update1DChart() {
    var chartElement = document.getElementById('sascalcChart').getContext('2d');
    var yDataSets = [
        {
            label: 'SASCALC',
            backgroundColor: window.chartColors.black,
            borderColor: window.chartColors.black,
            data: window.aveIntensity,
            fill: false
        }
    ]
    var dataOptions = {
        responsive: true,
        aspectRatio: 1.5,
        title: { display: false },
        tooltips: { mode: 'index', intersect: false, },
        hover: { mode: 'nearest', intersect: true },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: { display: true, labelString: "Q (Å^-1)" },
                // type: "logarithmic",
                ticks: { min: 0.000001, max: Math.max(window.qValues) * 1.1 , stepSize: 0.1 },
                autoSkip: true
            }],
            yAxes: [{
                display: true,
                offset: true,
                scaleLabel: { display: true, labelString: 'Relative Intensity (Au)' },
                // type: "logarithmic",
                ticks: { suggestedMin: 0.0001, suggestedMax: 10}
            }]
        },
        legend: {
            position: 'bottom',
            usePointStyle: true,
        }
    }
    var chart = new Chart(chartElement, {
        type: 'line',
        data: {
            labels: window.qValues,
            datasets: yDataSets
        },
        options: dataOptions
    });
    chart.update();
}

/*
 * Restore the persistant state on refresh
 */
function restorePersistantState() {
    // Load instrument and sample space
    var instrument = sessionStorage.getItem('instrument');
    if (instrument === "") {
        return;
    } else if (instrument === "vsans") {
        restoreVSANSstate();
    } else {
        var instSelector = document.getElementById('instrumentSelector');
        instSelector.value = instrument;
        updateInstrument('instrumentSelector', instrument, false);
        var sampleSpace = sessionStorage.getItem(instrument + 'SampleTable');
        var sampleSpaceNode = document.getElementById(instrument + 'SampleTable');
        sampleSpaceNode.value = sampleSpace;
        // Restore wavelength values
        var wavelengthSpread = sessionStorage.getItem(instrument + 'WavelengthSpread');
        var wavelength = sessionStorage.getItem(instrument + 'WavelengthInput');
        var wavelengthNode = document.getElementById(instrument + 'WavelengthInput');
        var wavelengthSpreadNode = document.getElementById(instrument + 'WavelengthSpread').value;
        wavelengthNode.value = wavelength;
        wavelengthSpreadNode.value = wavelengthSpread;
        updateWavelengthSpread(instrument, false);
        // Restore aperture and guide configuration values
        var customAperture = sessionStorage.getItem(instrument + 'CustomAperture');
        var sampleAperture = sessionStorage.getItem(instrument + 'SampleAperture');
        var guideConfig = sessionStorage.getItem(instrument + "GuideConfig");
        var customApertureNode = document.getElementById(instrument + 'CustomAperture');
        var sampleApertureSelectorNode = document.getElementById(instrument + 'SampleAperture');
        var guideNode = document.getElementById(instrument + 'GuideConfig');
        customApertureNode.value = customAperture;
        sampleApertureSelectorNode.value = sampleAperture;
        updateAperture(instrument, false);
        guideNode.value = guideConfig;
        updateGuides(instrument, guideConfig, false);
        // Restore detector distances
        var detectorDistance = sessionStorage.getItem(instrument + 'SDDInputBox');
        var detectorOffset = sessionStorage.getItem(instrument + 'OffsetInputBox');
        var detectorNode = document.getElementById(instrument + "SDDInputBox");
        var detectorSliderNode = document.getElementById(instrument + "SDDSliderBar");
        var offsetNode = document.getElementById(instrument + "OffsetInputBox");
        var offsetSliderNode = document.getElementById(instrument + "OffsetSliderBar");
        detectorNode.value = detectorDistance;
        detectorSliderNode.value = detectorDistance;
        offsetNode.value = detectorOffset;
        offsetSliderNode.value = detectorOffset;
        updateDetector(instrument, false);
    }
    // Run SASCALC at the end
    SASCALC(instrument);
}

/*
 * Placeholder for the VSANS persistant state restore function
 * TODO: Actually write this
 */
function restoreVSANSstate() {
    return;
}

/*
 * Store the persistant state for browser refreshes
 */
function storePersistantState(instrument) {
    // Store instrument and sample space
    sessionStorage.setItem('instrument', instrument);
    var sampleSpaceNode = document.getElementById(instrument + 'SampleTable');
    var sampleSelectStr = sampleSpaceNode.options[sampleSpaceNode.selectedIndex].value;
    sessionStorage.setItem(instrument + 'SampleTable', sampleSelectStr);
    // Store wavelength values
    var wavelength = document.getElementById(instrument + 'WavelengthInput');
    var wavelengthSpread = document.getElementById(instrument + 'WavelengthSpread').value;
    sessionStorage.setItem(instrument + 'WavelengthSpread', wavelengthSpread);
    sessionStorage.setItem(instrument + 'WavelengthInput', wavelength.value);
    // Store aperture and guide configuration values
    var customAperture = document.getElementById(instrument + 'CustomAperture');
    var sampleApertureSelector = document.getElementById(instrument + 'SampleAperture');
    var guideNode = document.getElementById(instrument + 'GuideConfig');
    var guideSelectStr = guideNode.options[guideNode.selectedIndex].value;
    sessionStorage.setItem(instrument + 'CustomAperture', customAperture.value);
    sessionStorage.setItem(instrument + 'SampleAperture', sampleApertureSelector.value);
    sessionStorage.setItem(instrument + "GuideConfig", guideSelectStr);
    // Store detector distances
    var detectorOutput = document.getElementById(instrument + "SDDInputBox");
    var offsetOutput = document.getElementById(instrument + "OffsetInputBox");
    sessionStorage.setItem(instrument + 'SDDInputBox', detectorOutput.value);
    sessionStorage.setItem(instrument + 'OffsetInputBox', offsetOutput.value);
}
