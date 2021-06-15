﻿function loadpage() {
    // Initialize data sets
    initializeData();
    clearFrozen(false);
    // Define base event handlers
    var instrumentNode = document.getElementById('instrumentSelector');
    instrumentNode.onchange = function () {
        updateInstrumentNoInstrument();
    }
    var modelNode = document.getElementById('model');
    modelNode.onchange = function () {
        selectModel(this.value);
    }
    var averagingNode = document.getElementById('averagingType');
    averagingNode.onchange = function () {
        selectAveragingMethod(this.value);
    }
    // Restore persistant state on refresh
    restorePersistantState();
};

function initializeData() {
    window.configNames = [];
    window.slicer = null;
    window.currentConfig = window.defaultConfiguration;
    window.qValues = new Array(1).fill(0);
    window.aveIntensity = new Array(1).fill(0);
    window.nCells = new Array(1).fill(0);
    window.dSQ = new Array(1).fill(0);
    window.sigmaAve = new Array(1).fill(0);
    window.qAverage = new Array(1).fill(0);
    window.sigmaQ = new Array(1).fill(0);
    window.fSubs = new Array(1).fill(0);
    window.qxValues = new Array(1).fill(0);
    window.qyValues = new Array(1).fill(0);
    window.intensity2D = new Array(1).fill(0);
}

/*
 * Run SASCALC for the current instrument and model
 */
function SASCALC(instrument) {
    // Initialize data sets
    initializeData();
    if (instrument == 'qrange') {
        // TODO: generate 1D and 2D data for a given q-range
    } else {
        // Calculate the beam stop diameter
        calculateBeamStopDiameter(instrument);
        // Calculate the estimated beam flux
        calculateBeamFlux(instrument);
        // Calculate the figure of merit
        calculateFigureOfMerit(instrument);
        // Calculate the number of attenuators
        calculateNumberOfAttenuators(instrument);
        // Do Circular Average of an array of 1s
        calculateQRangeSlicer(instrument);
        calculateMinimumAndMaximumQ(instrument);
    }
    // Do Circular Average of an array of 1s
    calculateModel();
    // Update the charts
    update1DChart();
    update2DChart();
    // Set current configuration
    setCurrentConfig(instrument);
    // Store persistant state
    storePersistantState(instrument);
}

/*
 * Calculate the q values for a given configuration
 */
function calculateQRange(instrument) {
    var xPixels = parseInt(window[instrument + "Constants"]["xPixels"]);
    var yPixels = parseInt(window[instrument + "Constants"]["yPixels"]);
    var xCenter = calculateXBeamCenter(instrument);
    var yCenter = yPixels / 2 + 0.5;
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]);
    var coeff = parseFloat(window[instrument + "Constants"]["coeff"]);
    var xDistance = yDistance = totalDistance = correctedDx = correctedDy = dataPixel = numDSquared = 0;
    var radiusCenter = 100;
    var numDimensions = center = largeNumber = 1;
    var i = j = k = l = nq = theta = thetaX = thetaY = radius = radX = radY = 0;
    var lambda = getWavelength(instrument);
    var includePixel = true;
    var averagingParams = getAveragingParams();
    var averageType = document.getElementById("averagingType").value;
    var phiRadians = (Math.PI / 180) * averagingParams[0] + Math.PI / 2;
    var dPhiRadians = (Math.PI / 180) * averagingParams[1];
    var phiUpper = phiRadians + dPhiRadians;
    var phiLower = phiRadians - dPhiRadians;
    var detectorHalves = averagingParams[2];
    var qCenter = averagingParams[3];
    var qWidth = averagingParams[4];
    var ratioAxes = averagingParams[5];

    // Detector values pixel size in mm
    var detectorDistance = parseFloat(document.getElementById(instrument + "SDDInputBox").value) * 10;
    var mask = generateStandardMask(instrument);
    var maskI = new Array();
    var data = generateOnesData(instrument);
    window.intensity2D = data;
    var dataI = new Array();

    // Loop over each pixel
    for (i = 0; i < xPixels; i++) {
        xDistance = calculateDistanceFromBeamCenter(i, xCenter, pixelSize, coeff);
        thetaX = Math.atan(xDistance / detectorDistance) / 2;
        window.qxValues[i] = (4 * Math.PI / lambda) * Math.sin(thetaX);
        maskI = mask[i];
        dataI = data[i];
        for (j = 0; j < yPixels; j++) {
            yDistance = calculateDistanceFromBeamCenter(j, yCenter, pixelSize, coeff);
            // Ignore masked pixels (mask[i][j] = 1)
            if (maskI[j] == 0) {
                dataPixel = dataI[j];
                totalDistance = Math.sqrt(xDistance * xDistance + yDistance * yDistance);
                // Break pixels up into a 3x3 grid close to the beam center
                if (totalDistance > radiusCenter) {
                    numDimensions = 1;
                    center = 1;
                } else {
                    numDimensions = 3;
                    center = 2;
                }
                numDSquared = numDimensions * numDimensions;
                thetaY = Math.atan(yDistance / detectorDistance) / 2;
                window.qyValues[j] = (4 * Math.PI / lambda) * Math.sin(thetaY);
                // Loop over sliced pixels
                for (k = 1; k <= numDimensions; k++) {
                    correctedDx = xDistance + (k - center) * pixelSize / numDimensions;
                    for (l = 1; l <= numDimensions; l++) {
                        correctedDy = yDistance + (l - center) * pixelSize / numDimensions;
                        // TODO: Replace all of this and create a Slicer object
                        // FIXME: Averaging isn't accurate for 1D data
                        switch (averageType) {
                            case "circular":
                            default:
                                var iRadius = Math.floor(Math.sqrt(correctedDx * correctedDx + correctedDy * correctedDy) / pixelSize) + 1;
                                includePixel = true;
                                break;
                            case "elliptical":
                                var rho = Math.atan(correctedDy / correctedDx) - phiRadians;
                                var iCircular = Math.floor(Math.sqrt(correctedDx * correctedDx + correctedDy * correctedDy) / pixelSize) + 1;
                                var iRadius = Math.floor(iCircular * Math.sqrt(Math.cos(rho) * Math.cos(rho) + ratioAxes * ratioAxes * Math.sin(rho) * Math.sin(rho))) + 1
                                includePixel = true;
                                break;
                            case "sector":
                                // Get raw angle
                                // FIXME: rotate calculation by 90 degrees...
                                var pixelAngle = Math.atan(Math.abs(correctedDy) / Math.abs(correctedDx)) + Math.PI / 2;
                                var isCorrectAngle = (pixelAngle > phiLower) && (pixelAngle < phiUpper);
                                var isCorrectAngleMirror = (pixelAngle > phiLower) && (pixelAngle < phiUpper);
                                var forward = (isCorrectAngle && correctedDx > 0);
                                var mirror = (isCorrectAngleMirror && correctedDx < 0);
                                var iRadius = Math.floor(Math.sqrt(correctedDx * correctedDx + correctedDy * correctedDy) / pixelSize) + 1;
                                var both = (detectorHalves == "both" && (mirror || forward));
                                var left = (detectorHalves == "left" && mirror);
                                var right = (detectorHalves = "right" && forward);
                                if (both || right || left) {
                                    includePixel = true;
                                } else {
                                    includePixel = false;
                                }
                                break;
                            case "annular":
                                // TODO: Actually write this.
                                break;
                            case "rectangular":
                                var correctedRadius = Math.sqrt(correctedDx * correctedDx + correctedDy * correctedDy);
                                var dotProduct = (correctedDx * phiX + correctedDy * phiY) / correctedRadius;
                                var forward = (dotProduct > 1);
                                var mirror = !forward;
                                var dPhiPixel = Math.acos(dotProduct);
                                var dPerp = correctedRadius * Math.sin(dPhiPixel);
                                var dParallel = correctedRadius * Math.cos(dPhiPixel);
                                var iRadius = Math.floor(Math.abs(dParallel) / pixelSize) + 1;
                                if ((dPerp <= 0.5 * qWidth * pixelSize) && (detectorHalves == "both" || (detectorHalves = "left" && mirror) || (detectorHalves == "right" && forward))) {
                                    includePixel = true;
                                } else {
                                    includePixel = false;
                                }
                                break;
                        }
                        if (includePixel) {
                            nq = (iRadius > nq) ? iRadius : nq;
                            calculateIntensityValues(iRadius, dataPixel, numDSquared);
                        }
                    }
                }
            }
        }
    }

    var ntotal = aveSQ = aveisq = diff = 0;
    // Loop over every q value
    for (i = 0; i <= nq; i++) {
        radius = (2 * i) * pixelSize / 2;
        theta = Math.atan(radius / detectorDistance) / 2;
        window.qValues[i] = (4 * Math.PI / lambda) * Math.sin(theta);
        if (window.nCells[i] <= 1) {
            window.aveIntensity[i] = (window.nCells[i] == 0 || Number.isNaN(window.nCells[i])) ? 0 : window.aveIntensity[i] / window.nCells[i];
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

function calculateQRangeSlicer(instrument) {
    var xPixels = parseInt(window[instrument + "Constants"]["xPixels"]);
    var yPixels = parseInt(window[instrument + "Constants"]["yPixels"]);
    var xCenter = calculateXBeamCenter(instrument);
    var yCenter = yPixels / 2 + 0.5;
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]);
    var coeff = parseFloat(window[instrument + "Constants"]["coeff"]);
    var averageType = document.getElementById("averagingType").value;
    var lambda = getWavelength(instrument);
    var apertureOffset = parseFloat(window[instrument + "Constants"]["ApertureOffset"]);

    // Detector values pixel size in mm
    var detectorDistance = parseFloat(document.getElementById(instrument + "SDDInputBox").value) * 10;
    window.intensity2D = generateOnesData(instrument);
    window.mask = generateStandardMask(instrument);

    // Calculate Qx and Qy values
    for (var i = 0; i < xPixels; i++) {
        var xDistance = calculateDistanceFromBeamCenter(i, xCenter, pixelSize, coeff);
        var thetaX = Math.atan(xDistance / detectorDistance) / 2;
        window.qxValues[i] = (4 * Math.PI / lambda) * Math.sin(thetaX);
    }
    for (var i = 0; i < yPixels; i++) {
        yDistance = calculateDistanceFromBeamCenter(i, yCenter, pixelSize, coeff);
        var thetaY = Math.atan(yDistance / detectorDistance) / 2;
        window.qyValues[i] = (4 * Math.PI / lambda) * Math.sin(thetaY);
    }

    var averagingParams = getAveragingParams();
    var params = {};
    params['phi'] = (Math.PI / 180) * averagingParams[0];
    params['dPhi'] = (Math.PI / 180) * averagingParams[1];
    params['detectorSections'] = averagingParams[2];
    params['qCenter'] = averagingParams[3];
    params['qWidth'] = averagingParams[4];
    params['aspectRatio'] = averagingParams[5];
    params['lambda'] = lambda;
    params['xBeamCenter'] = xCenter;
    params['yBeamCenter'] = yCenter;
    params['pixelSize'] = parseFloat(window[instrument + "Constants"]["aPixel"]);
    params['coeff'] = parseFloat(window[instrument + "Constants"]["coeff"]);
    params['lambdaWidth'] = getWavelengthSpread(instrument);
    params['guides'] = document.getElementById(instrument + "GuideConfig").value;
    params['sourceAperture'] = getSourceAperture(instrument) * 0.5;
    params['sampleAperture'] = getSampleApertureSize(instrument) * 0.5;
    params['apertureOffset'] = apertureOffset;
    params['beamStopSize'] = calculateBeamStopDiameter(instrument) * 2.54;
    params['SSD'] = calculateSourceToSampleApertureDistance(instrument);
    params['SDD'] = calculateSampleToDetectorDistance(instrument);

    switch (averageType) {
        case "circular":
        default:
            window.slicer = new Circular(params);
            break;
        case "sector":
            window.slicer = new Sector(params);
            break;
        case "rectangular":
            window.slicer = new Rectangular(params);
            break;
        case "elliptical":
            window.slicer = new Elliptical(params);
            break;
    }
    window.slicer.calculate();
}

/*
 * Calculate the minimum and maximum Q-values for the given configuration
 */
function calculateMinimumAndMaximumQ(instrument) {
    calculateMinimumQ(instrument);
    calculateMaximumQ(instrument);
    calculateMaximumVerticalQ(instrument);
    calculateMaximumHorizontalQ(instrument);
}

/*
 * Calculate Q-maximum at the corner(s) of the detector
 */
function calculateMaximumQ(instrument) {
    var SDD = calculateSampleToDetectorDistance(instrument);
    var offset = parseFloat(document.getElementById(instrument + "OffsetInputBox").value);
    var lambda = getWavelength(instrument);
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]) * 0.1;
    var xPixels = parseFloat(window[instrument + "Constants"]["xPixels"]);
    var detWidth = pixelSize * xPixels;

    // Calculate Q-maximum and populate the page
    var radial = Math.sqrt(Math.pow(0.5 * detWidth, 2) + Math.pow(0.5 * detWidth + offset, 2));
    var qMaximum = (4 * (Math.PI / lambda) * Math.sin(0.5 * Math.atan(radial / SDD)));
    var qMaxNode = document.getElementById(instrument + "MaximumQ");
    qMaxNode.value = Math.round(qMaximum*100000) / 100000;
}

/*
 * Calculate Q-maximum at the top/bottom of the detector
 */
function calculateMaximumVerticalQ(instrument) {
    var SDD = calculateSampleToDetectorDistance(instrument);
    var lambda = getWavelength(instrument);
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]) * 0.1;
    var xPixels = parseFloat(window[instrument + "Constants"]["xPixels"]);
    var detWidth = pixelSize * xPixels;

    // Calculate Q-maximum and populate the page
    var theta = Math.atan((detWidth / 2.0) / SDD);
    var qMaxVert = (4 * (Math.PI / lambda) * Math.sin(0.5 * theta));
    var qMaxVertNode = document.getElementById(instrument + "MaximumVerticalQ");
    qMaxVertNode.value = Math.round(qMaxVert * 100000) / 100000;
}

/*
 * Calculate Q-maximum at the left/right edge of the detector
 */
function calculateMaximumHorizontalQ(instrument) {
    var SDD = calculateSampleToDetectorDistance(instrument);
    var offset = parseFloat(document.getElementById(instrument + "OffsetInputBox").value);
    var lambda = getWavelength(instrument);
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]) * 0.1;
    var xPixels = parseFloat(window[instrument + "Constants"]["xPixels"]);
    var detWidth = pixelSize * xPixels;

    // Calculate Q-maximum and populate the page
    var theta = Math.atan((detWidth / 2.0 + offset) / SDD);
    var qMaxHorizon = (4 * (Math.PI / lambda) * Math.sin(0.5 * theta));
    var qMaxHorizonNode = document.getElementById(instrument + "MaximumHorizontalQ");
    qMaxHorizonNode.value = Math.round(qMaxHorizon * 100000) / 100000;
}

/*
 * Calculate Q-minimum, accounting for the beam stop
 */
function calculateMinimumQ(instrument) {
    var SDD = calculateSampleToDetectorDistance(instrument);
    var bsProjection = calculateProjectedBeamStopDiameter(instrument);
    var lambda = getWavelength(instrument);
    var pixelSize = parseFloat(window[instrument + "Constants"]["aPixel"]) * 0.1;
    // Calculate Q-minimum and populate the page
    var qMinimum = ((Math.PI / lambda) * (bsProjection + pixelSize + pixelSize) / SDD);
    var qMinNode = document.getElementById(instrument + "MinimumQ");
    qMinNode.value = Math.round(qMinimum * 100000) / 100000;
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
function calculateXBeamCenter(instrument) {
    // Find the number of x pixels in the detector
    var xPixels = parseInt(window[instrument + "Constants"]["xPixels"]);
    // Get pixel size in mm and convert to cm
    var dr = parseFloat(window[instrument + "Constants"]["aPixel"]) / 10;
    // Get detector offset in cm
    var offset = parseFloat(document.getElementById(instrument + "OffsetInputBox").value);
    var xCenter = (offset / dr) + (xPixels / 2 + 0.5);
    return xCenter;
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
    var lambda = getWavelength(instrument);
    var lambdaWidth = getWavelengthSpread(instrument);
    var isLenses = Boolean(document.getElementById(instrument + "GuideConfig") === "LENS");
    // Get values and be sure they are in cm
    var sourceApertureRadius = getSourceAperture(instrument) * 0.5;
    var sampleApertureRadius = getSampleApertureSize(instrument) * 0.5;
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
    var smallNumber = 1e-10;
    // Base calculations
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

    // FIXME: Find usable incomplete gamma function in javascript (or php)
    var incGamma = smallNumber;
    //if (rZero < beamStopSize) {
    //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 - gammainc(1.5, delta) / math.gamma(1.5));
    //} else {
    //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 + window.gammainc(1.5, delta) / math.gamma(1.5));
    //}
    var fSubS = 0.5 * (1.0 + math.erf((rZero - beamStopSize) / Math.sqrt(2.0 * varDetector)));
    if (fSubS <= 0.0) {
        fSubS = smallNumber;
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
    var beamFluxNode = document.getElementById(instrument + 'BeamFlux');
    
    // Get instrumental values
    var SSD = calculateSourceToSampleApertureDistance(instrument);
    var sourceAperture = getSourceAperture(instrument);
    var sampleAperture = getSampleApertureSize(instrument);
    var lambda = getWavelength(instrument);
    var lambdaWidth = getWavelengthSpread(instrument) / 100;
    var numGuides = getNumberOfGuides(instrument);

    // Get constants
    var peakFlux = parseFloat(window[instrument + 'Constants']['peakFlux']);
    var peakLambda = parseFloat(window[instrument + 'Constants']['peakLambda']);
    var guideGap = parseFloat(window[instrument + 'Constants']['guideGap']);
    var guideLoss = parseFloat(window[instrument + 'Constants']['guideLoss']);
    var guideWidth = parseFloat(window[instrument + 'Constants']['guideWidth']);
    var trans1 = parseFloat(window[instrument + 'Constants']['trans1']);
    var trans2 = parseFloat(window[instrument + 'Constants']['trans2']);
    var trans3 = parseFloat(window[instrument + 'Constants']['trans3']);
    var b = parseFloat(window[instrument + 'Constants']['b']);
    var c = parseFloat(window[instrument + 'Constants']['c']);

    // Run calculations
    var alpha = (sourceAperture + sampleAperture) / (2 * SSD);
    var f = guideGap * alpha / (2 * guideWidth);
    var trans4 = (1 - f) * (1 - f);
    var trans5 = Math.exp(numGuides * Math.log(guideLoss));
    var trans6 = 1 - lambda * (b - (numGuides / 8) * (b - c));
    var totalTrans = trans1 * trans2 * trans3 * trans4 * trans5 * trans6;

    var area = Math.PI * sampleAperture * sampleAperture / 4;
    var d2_phi = peakFlux / (2 * Math.PI);
    d2_phi *= Math.exp(4 * Math.log(peakLambda / lambda));
    d2_phi *= Math.exp(-1 * (Math.pow(peakLambda  / lambda, 2)));
    var solid_angle = (Math.PI / 4) * (sourceAperture / SSD) * (sourceAperture / SSD);
    var beamFlux = Math.round(area * d2_phi * lambdaWidth * solid_angle * totalTrans);

    beamFluxNode.value = beamFlux;
    return parseFloat(beamFluxNode.value);
}

/*
 * Calculate the estimated beam flux
 */
function calculateFigureOfMerit(instrument) {
    var lambda = getWavelength(instrument);
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
    var aPixel = parseFloat(window[instrument + "Constants"]["aPixel"]) / 10;
    var iPixelMax = parseFloat(window[instrument + "Constants"]["iPixel"]);
    var num_pixels = (Math.PI / 4) * (0.5 * (a2 + beamDiam)) * (0.5 * (a2 + beamDiam)) / (aPixel * aPixel);
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
    var wavelength = getWavelength(instrument);

    var af = 0.498 + 0.0792 * wavelength - 1.66e-3 * wavelength * wavelength;
    var nf = -Math.log(atten) / af;
    var numAtten = Math.floor(nf) + 1;
    if (numAtten > 6) {
        numAtten = 7 + Math.floor((numAtten - 6) / 2);
    }
    attenuatorNode.value = numAtten;
    getAttenuators(instrument);
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
    return bsDiam; // Return value is in inches
}

/*
 * Calculate the size of the beam stop as projected onto the detector
 */
function calculateProjectedBeamStopDiameter(instrument) {
    var bsDiam = calculateBeamStopDiameter(instrument) * 2.54;
    var SDD = calculateSampleToDetectorDistance(instrument);
    var sampleAperture = getSampleApertureSize(instrument);
    var apertureOffset = parseFloat(window[instrument + 'Constants']['ApertureOffset']);

    var L2 = SDD + apertureOffset;
    var LBeamstop = 20.1 + 1.61 * bsDiam; //distance in cm from beamstop to anode plane (empirical)
    return bsDiam + (bsDiam + sampleAperture) * LBeamstop / (L2 - LBeamstop); // Return value is in cm
}

/*
 * Calculate the beam diameter at the detector
 */
function calculateBeamDiameter(instrument, direction = 'maximum') {
    // Get values for the desired instrument
    var a1 = getSourceAperture(instrument);
    var l1 = calculateSourceToSampleApertureDistance(instrument);
    var l2 = calculateSampleToDetectorDistance(instrument)
    if (document.getElementById(instrument + 'GuideConfig').value === 'LENS') {
        // If LENS configuration, the beam size is the source aperture size
        return a1;
    }
    var a2 = getSampleApertureSize(instrument);
    var lambda = getWavelength(instrument);
    var lambdaDelta = getWavelengthSpread(instrument) / 100.0;
    var bsFactor = parseFloat(window[instrument + 'Constants']['BSFactor']);
    // Calculate beam size on the detector
    var d1 = a1 * l2 / l1;
    var d2 = a2 * (l1 + l2) / l1;
    // Beam width
    var bw = d1 + d2;
    // Beam height due to gravity
    var bv = bw + 1.25e-8 * (l1 + l2) * l2 * lambda * lambda * lambdaDelta;
    // Larger of the width*safetyFactor and height
    var bm_bs = bsFactor * bw;
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
    // Get the number of guides
    var nGds = getNumberOfGuides(instrument);
    // Get the source to sample distance node
    var SSD = document.getElementById(instrument + "SSD");
    // Get the sample location
    var sampleSpace = document.getElementById(instrument + 'SampleTable').value;
    var ssd = 0.0;
    var ssdOffset = parseFloat(window[instrument + 'Constants'][sampleSpace + 'Offset']);
    var apertureOffset = parseFloat(window[instrument + 'Constants']['ApertureOffset']);
    // Calculate the source to sample distance
    switch (instrument) {
        case 'ng7':
        case 'ngb30':
            ssd = 1632 - 155 * nGds - ssdOffset - apertureOffset;
            break;
        case 'ngb10':
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
 * Use the updated aperture values to calculate the Q ranges for the current instrument
 */
function updateAperture(instrument, runSASCALC = true) {
    // Get aperture nodes for the specific instrument
    var customAperture = document.getElementById(instrument + 'CustomAperture');
    var customApertureLabel = document.getElementById(instrument + 'CustomApertureLabel');
    var sampleApertureSelector = document.getElementById(instrument + 'SampleAperture');
    // Show/hide custom aperture size box
    if (sampleApertureSelector.value === "Custom") {
        // TODO: Allow different aperture shapes
        customAperture.style.display = 'inline-block';
        customApertureLabel.style.display = 'inline-block';
        window.currentConfig["geometry.externalSampleAperture"] = customAperture.value;

    } else {
        customAperture.style.display = 'none';
        customApertureLabel.style.display = 'none';
        window.currentConfig["geometry.externalSampleAperture"] = sampleApertureSelector.value;
        window.currentConfig["geometry.externalSampleApertureShape"] = "CIRCLE";

    }
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Use the updated wavelength spread to determine the allowed wavelength range
 */
function updateWavelength(instrument, runSASCALC=true) {
    var wavelength = getWavelength(instrument);
    var wavelengthSpread = getWavelengthSpread(instrument);
     var wavelengthOptions = window[instrument + 'WavelengthRange'][wavelengthSpread];
    try {
        wavelength.min = parseFloat(wavelengthOptions[0]);
        wavelength.max = parseFloat(wavelengthOptions[1]);
    } catch (err) {
        wavelengthOptions = ['4.0', '20.0'];
    }
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Change the instrument you want to calculate Q ranges for
 */
function updateInstrumentNoInstrument(runSASCALC = true) {
    var instrument = document.getElementById('instrumentSelector').value;
    updateInstrument(instrument, runSASCALC);
}
/*
 * Change the instrument you want to calculate Q ranges for
 */
function updateInstrument(instrument, runSASCALC=true) {
    // Get instrument node and create an array of the options available
    var inst = document.getElementById('instrumentSelector');
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
        if (key === instrument) {
            instruments[key].style.display = "block";
        } else {
            instruments[key].style.display = "none";
        }
    }
    if (instrument != '' && instrument != null) {
        var serverNameNode = document.getElementById('serverName');
        serverNameNode.value = window[instrument + "Constants"]['serverName'];
        var buttons = document.getElementById('buttons');
        buttons.style.display = "inline-block";
        var model = document.getElementById("model");
        model.style.display = "inline-block";
        selectModel(model.value, false);
        var modelLabel = document.getElementById("modelLabel");
        modelLabel.style.display = "inline-block";
        var modelParams = document.getElementById("modelParams");
        modelParams.style.display = "inline-block";
        var averagingType = document.getElementById("averagingType");
        averagingType.style.display = "inline-block";
        var averagingTypeLabel = document.getElementById("averagingTypeLabel");
        averagingTypeLabel.style.display = "inline-block";
        selectAveragingMethod(averagingType.value, false);
        try {
            populatePageDynamically(instrument);
        } catch (error) {
            console.info("Unable to connect to the instrument. Using standard values and limits.")
        }
        setEventHandlers(instrument);
        // Run SASCALC
        if (runSASCALC) {
            SASCALC(instrument);
        }
    }
}
/*
 * Set the event handlers for the current active instrument
 */
function setEventHandlers(instrument) {
    // Initialize oninput and onchange events for the given instrument
    var sampleTableNode = document.getElementById(instrument + 'SampleTable');
    sampleTableNode.onchange = function () { SASCALC(instrument); }
    var wavelengthNode = document.getElementById(instrument + 'WavelengthInput');
    wavelengthNode.onchange = function () { updateWavelength(instrument); }
    var wavelengthSpreadNode = document.getElementById(instrument + 'WavelengthSpread');
    wavelengthSpreadNode.onchange = function () { updateWavelength(instrument); }
    var guideConfigNode = document.getElementById(instrument + 'GuideConfig');
    guideConfigNode.onchange = function () { updateGuides(instrument, this.value); }
    var apertureSourceNode = document.getElementById(instrument + 'SourceAperture');
    apertureSourceNode.onchange = function () { SASCALC(instrument); }
    var apertureSampleNode = document.getElementById(instrument + 'SampleAperture');
    apertureSampleNode.onchange = function () { updateAperture(instrument); }
    var apertureSampleCustomNode = document.getElementById(instrument + 'CustomAperture');
    apertureSampleCustomNode.onchange = function () { updateAperture(instrument); }
    var detectorSlider = document.getElementById(instrument + "SDDSliderBar");
    detectorSlider.onchange = function () { detectorOutput.value = this.value; SASCALC(instrument); }
    var detectorOutput = document.getElementById(instrument + "SDDInputBox");
    detectorOutput.oninput = function () { detectorSlider.value = this.value; SASCALC(instrument); }
    var offsetSlider = document.getElementById(instrument + "OffsetSliderBar");
    offsetSlider.onchange = function () { offsetOutput.value = this.value; SASCALC(instrument); }
    var offsetOutput = document.getElementById(instrument + "OffsetInputBox");
    offsetOutput.oninput = function () { offsetSlider.value = this.value; SASCALC(instrument); }
    // Initialize onclick events for freezing and clearing calculations
    var freezeButton = document.getElementById("freezeButton");
    freezeButton.onclick = function () { freezeSASCALC(); }
    var clearFrozenButton = document.getElementById("clearFrozenButton");
    clearFrozenButton.onclick = function () { clearFrozen(); }

    // Initialize routine when button is displayed:
    var send_button = document.getElementById('sendToNICE');
    send_button.onclick = async function () { connectToNice(sendConfigsToNice); }
}
/*
 * Attempt to populate the page using values taken directly from the instrument
 * Any failed connections will cause the page to use the default values for all inputs
 */
async function populatePageDynamically(instrument) {
    var staticNodeMap = await connectToNice(getStaticNodeMap);
    var deviceMap = await connectToNice(getDevicesMap);
    // Available wavelength spreads
    var wavelengthSpreads = staticNodeMap['wavelengthSpread.wavelengthSpread']['permittedValues'];
    var wavelengthSpreadNode = document.getElementById(instrument + 'WavelengthSpread');
    if (wavelengthSpreads != null && typeof wavelengthSpreads[Symbol.iterator] === 'function') {
        while (wavelengthSpreadNode.lastChild) {
            wavelengthSpreadNode.removeChild(wavelengthSpreadNode.lastChild);
        }
        for (var wavelengthSpread in wavelengthSpreads) {
            var spread = wavelengthSpreads[wavelengthSpread];
            var option = document.createElement("OPTION");
            var val = Math.round(1000 * parseFloat(spread.val)) / 10;
            option.value = val;
            option.appendChild(document.createTextNode(val));
            wavelengthSpreadNode.appendChild(option);
        }
    }
    // TODO: Populate GUIDES, SOURCE APERTURES, and DETECTOR LIMITS (and wavelenth limits?)
    var sourceApertures = staticNodeMap['guide.sourceAperture']['permittedValues'];
    var sourceAperturesGuide1 = staticNodeMap['guide01.key']['permittedValues'];
}

/*
 * Update the page when a new model is selected
 */
function selectModel(model, runSASCALC = true) {
    var modelParams = document.getElementById("modelParams");
    // Show the node
    modelParams.style.display = "inline-block";
    // Remove existing nodes
    while (modelParams.lastChild) {
        modelParams.removeChild(modelParams.lastChild);
    }
    var instrument = document.getElementById('instrumentSelector').value;
    var params = window.modelList[model]["params"];
    var paramNames = Object.keys(params);
    var defaultValues = Object.values(params);
    // Create new nodes for parameters
    for (var i = 0; i < paramNames.length; i++) {
        var id = model + "_" + paramNames[i];
        var label = document.createElement("LABEL");
        var for_att = document.createAttribute("for");
        for_att.value = id;
        label.setAttributeNode(for_att);
        label.innerHTML = paramNames[i].charAt(0).toUpperCase() + paramNames[i].slice(1) + ": ";
        var input = document.createElement("input");
        var id_att = document.createAttribute("id");
        id_att.value = id;
        input.setAttributeNode(id_att);
        input.value = defaultValues[i];
        input.oninput = function () { SASCALC(instrument); }
        modelParams.appendChild(label);
        modelParams.appendChild(input);
    }
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Update the page when a new averaging method is selected
 */
function selectAveragingMethod(averagingMethod, runSASCALC = true) {
    var inputs = window.averagingInputs[averagingMethod];
    var paramNodes = document.getElementById("averagingParams");
    paramNodes.onchange = function () {
        var instrument = document.getElementById('instrumentSelector').value;
        SASCALC(instrument);
    }
    var params = paramNodes.children;
    for (var i = 0; i < params.length; i++) {
        var node = params[i];
        if (inputs.includes(node.getAttribute('for')) || inputs.includes(node.getAttribute('id'))) {
            node.style.display = "inline-block";
        } else {
            node.style.display = "none";
        }
    }
    // TODO: Add averaging representation to 2D heatmap (sector lines, ellipse, etc.)
    if (runSASCALC) {
        var instrument = document.getElementById('instrumentSelector').value;
        SASCALC(instrument);
    }
}

/*
 * Various getter functions - set current config on get
 */
function getWavelength(instrument) {
    var lambda = parseFloat(document.getElementById(instrument + "WavelengthInput").value);
    return lambda;
}
function getWavelengthSpread(instrument) {
    var wavelengthSpread = parseFloat(document.getElementById(instrument + "WavelengthSpread").value);
    return wavelengthSpread;
}
function getAttenuators(instrument) {
    var attenuators = parseFloat(document.getElementById(instrument + "Attenuators").value);
    return attenuators;
}
function getSourceAperture(instrument) {
    var sourceAperture = parseFloat(document.getElementById(instrument + "SourceAperture").value);
    return sourceAperture;
}
function getSampleApertureSize(instrument) {
    var sampleApertureRawValue = document.getElementById(instrument + 'SampleAperture').value;
    var sampleApertureCalculations = 0.0;
    if (sampleApertureRawValue === 'Custom') {
        sampleApertureCalculations = parseFloat(document.getElementById(instrument + 'CustomAperture').value);
    } else {
        // Default values in inches - convert to cm for calculations 
        sampleApertureCalculations = parseFloat(sampleApertureRawValue) * 2.54;
    }
    return sampleApertureCalculations;
}
function getNumberOfGuides(instrument) {
    var guides = document.getElementById(instrument + 'GuideConfig').value;
    if (guides === "LENS") {
        guides = "0";
    }
    return parseFloat(guides);
}
function getAveragingParams() {
    var phi = parseFloat(document.getElementById('phi').value);
    var dPhi = parseFloat(document.getElementById('dPhi').value);
    var detectorHalves = document.getElementById('detectorSections').value;
    var qCenter = parseFloat(document.getElementById('qCenter').value);
    var qWidth = parseFloat(document.getElementById('qWidth').value);
    var aspectRatio = parseFloat(document.getElementById('aspectRatio').value);
    var params = [phi, dPhi, detectorHalves, qCenter, qWidth, aspectRatio];
    return params;
}
function setCurrentConfig(instrument) {
    window.currentConfig["guide.guide"] = document.getElementById(instrument + 'GuideConfig').value;
    window.currentConfig["geometry.externalSampleAperture"] = getSampleApertureSize(instrument) * 10 + window.units["sampleAperture"];
    window.currentConfig["guide.sourceAperture"] = getSourceAperture(instrument);
    window.currentConfig["attenuator.key"] = getAttenuators(instrument);
    window.currentConfig["wavelength.wavelength"] = getWavelength(instrument) + window.units["wavelength"];
    window.currentConfig["wavelengthSpread.wavelengthSpread"] = getWavelengthSpread(instrument) / 100;
    window.currentConfig["areaDetector.beamCenterY"] = parseInt(window[instrument + "Constants"]["yPixels"]) / 2 + 0.5 + window.units["beamCenter"];
    window.currentConfig["areaDetector.beamCenterX"] = (Math.round(calculateXBeamCenter(instrument) * 1000) / 1000) + window.units["beamCenter"];
    window.currentConfig["beamStop.beamStop"] = calculateBeamStopDiameter(instrument);
    window.currentConfig["geometry.sampleToAreaDetector"] = document.getElementById(instrument + "SDDInputBox").value + window.units["detectorDistance"];
    window.currentConfig["detectorOffset.softPosition"] = document.getElementById(instrument + "OffsetInputBox").value + window.units["detectorOffset"];
}

/*
 * Freeze the current calculation
 */
function freezeSASCALC() {
    var frozen = new Array(1).fill(0);
    // Offset intensities of frozen configs by a factor of 2
    var intensities = new Array(1).fill(0);
    var n = 2 * (window.frozenCalculations.length + 1);
    for (var i = 0; i < window.aveIntensity.length; i++) {
        intensities[i] = n * window.aveIntensity[i];
    }
    frozen[0] = window.qValues;
    frozen[1] = intensities;
    frozen[2] = window.nCells;
    frozen[3] = window.dSQ;
    frozen[4] = window.sigmaAve;
    frozen[5] = window.qAverage;
    frozen[6] = window.sigmaQ;
    frozen[7] = window.fSubs;
    frozen[8] = window.qxValues;
    frozen[9] = window.qyValues;
    frozen[10] = window.intensity2D;
    window.frozenCalculations.push(frozen);
    var configName = generateConfigName(window.currentConfig);
    window.frozenConfigs[configName] = Object.assign({}, window.currentConfig);
    update1DChart();
    var instrument = document.getElementById('instrumentSelector').value;
    storePersistantState(instrument);
}

/*
 * Clear all frozen calculations
 */
function clearFrozen(update=true) {
    window.frozenCalculations = [];
    window.frozenConfigs = {};
    if (update) {
        update1DChart();
        var instrument = document.getElementById('instrumentSelector').value;
        storePersistantState(instrument);
    }
}
