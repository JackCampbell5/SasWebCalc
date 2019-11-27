function loadpage() {
    // TODO: only need a single chart
    var ngb30ctx = document.getElementById('ngb30SansChart').getContext('2d');
    var ngb10ctx = document.getElementById('ngb10SansChart').getContext('2d');
    var ng7ctx = document.getElementById('ng7SansChart').getContext('2d');
    var vctx = document.getElementById('vsansChart').getContext('2d');
    // TODO: Create real base data sets
    var sansDataSets = [
        {
            label: 'Data',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        }
    ]
    var vsansDataSets = [
        {
            label: 'Sample 1 - FT',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - FB',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - FL',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - FR',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - MT',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - MB',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - ML',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - MB',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        },
        {
            label: 'Sample 1 - B',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [12, 19, 3, 5, 2, 3],
            fill: false
        }
    ]

    var options = {
        responsive: true,
        title: {display: false },
        tooltips: {mode: 'index', intersect: false,},
        hover: {mode: 'nearest', intersect: true},
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: { display: true, labelString: "Q (Å^-1)"}
            }],
            yAxes: [{
                display: true,
                scaleLabel: { display: true, labelString: 'Relative Intensity (Au)'},
                ticks: {suggestedMin: 0, suggestedMax: 100, suggestedStepSize: 5}
            }]
        }
    }

    update1DChart(ngb30ctx, [0, 1, 2, 3, 4, 5], sansDataSets, options);
    update1DChart(ngb10ctx, [0, 1, 2, 3, 4, 5], sansDataSets, options);
    update1DChart(ng7ctx, [0, 1, 2, 3, 4, 5], sansDataSets, options);
    update1DChart(vctx, [0, 1, 2, 3, 4, 5], vsansDataSets, options);
    //restorePersistantState();
};

/*
 * Run SASCALC for the current instrument and model
 */
function SASCALC(instrument, model="Debye") {
    // Calculate the beam stop diameter
    var bsDiam = calculateBeamStopDiameter(instrument);

    // TODO: Run calculation, update charts, etc.
    // TODO: Do Circular Average of an array of 1s
    // TODO: Calculate model in Q range
}

/*
 * Calculate the q values for a given configuration
 */
function calculateQRange(instrument) {
    // TODO: Run calculation
}

/*
 * Calculate the beam stop diameter needed to cover the beam
 */
function calculateBeamStopDiameter(instrument) {
    if (document.getElementById(instrument + 'GuideConfig').value === 'LENS') {
        // If LENS configuration, the beam size is the source aperture size
        return 1;
    } else {
        var bm = calculateBeamDiameter(instrument, 'maximum');
        // TODO: ngb10m has 1.5" BS, but no 2"
        var bsDiam = Math.ceil(bm / 2.54);
    }
    return bsDiam;
}

/*
 * Calculate the beam diameter at the detector
 */
function calculateBeamDiameter(instrument, direction='maximum') {
    // Get values for the desired instrument
    var a1 = parseFloat(document.getElementById(instrument + 'SourceAperture').value);
    if (document.getElementById(instrument + 'GuideConfig').value === 'LENS') {
        // If LENS configuration, the beam size is the source aperture size
        return a1;
    }
    var sampleAperture = document.getElementById(instrument + 'SampleAperture').value;
    if (sampleAperture === 'Custom') {
        var a2 = parseFloat(document.getElementById(instrument + 'CustomAperture').value);
    } else {
        // Default values in inches - convert to cm
        var a2 = parseFloat(sampleAperture) * 2.54;
    }
    var lambda = parseFloat(document.getElementById(instrument + 'WavelengthInput').value);
    var lambdaDelta = parseFloat(document.getElementById(instrument + 'WavelengthSpread').value) / 100.0;
    var l1 = calculateSourceToSampleDistance(instrument);
    var sdd = parseFloat(document.getElementById(instrument + 'SDDInputBox').value);
    var sampleSpace = document.getElementById(instrument + 'SampleTable').value;
    var sddOffset = parseFloat(window[instrument + 'Constants'][sampleSpace + 'Offset']);
    var bsFactor = parseFloat(window[instrument + 'Constants']['BSFactor']);
    // Calculate beam size on the detector
    var l2 = sdd + sddOffset;
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
 *  Calculate the source to sample distance
 */
function calculateSourceToSampleDistance(instrument) {
    // Get the number of guides
    var guides = document.getElementById(instrument + 'GuideConfig').value;
    if (guides === "LENS") {
        guides = "0";
    }
    var nGds = parseFloat(guides);
    // Get the sample location
    var sampleSpace = document.getElementById(instrument + 'SampleTable').value;
    var ssd = 0.0;
    var ssdOffset = parseFloat(window[instrument + 'Constants'][sampleSpace + 'Offset']);
    // Calculate certain offsets based on the sample location
    if (sampleSpace === 'Huber') {
        ssdOffset += parseFloat(window[instrument + 'Constants']['ChamberOffset']);
    }
    // Calculate the source to sample distance
    switch (instrument) {
        case 'ng7':
        case 'ngb30m':
            ssd = 1632 - 155 * nGds - ssdOffset;
            break;
        case 'ngb10m':
            if (nGds == 0) {
                ssd = 513 - ssdOffset;
            } else {
                ssd = 513 - 61.9 - 150 * nGds - ssdOffset;
            }
            break;
        default:
            ssd = 0.0;
    }
    return ssd;
}

/*
 * Use the updated guide values to calculate the Q ranges for the current instrument
 */
function updateGuides(instrument, guideSelectStr) {
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
    // Store the guide configuration to the persistant state
    sessionStorage.setItem(instrument + "GuideConfig", guideSelectStr);
    // Recalculate q range
    SASCALC(instrument);
};

/*
 * Use the updated detector values to calculate the Q ranges for the current instrument
 */
function updateDetector(instrument) {
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
    // Recalculate q range
    SASCALC(instrument);
}

/*
 * Use the updated aperture values to calculate the Q ranges for the current instrument
 */
function updateAperture(instrument) {
    // Get aperture nodes for the specific instrument
    var instStr = instrument.toString();
    var customAperture = document.getElementById(instStr + 'CustomAperture');
    var customApertureLabel = document.getElementById(instStr + 'CustomApertureLabel');
    var sampleApertureSelector = document.getElementById(instStr + 'SampleAperture');
    // Show/hide custom aperture size box
    if (sampleApertureSelector.value === "Custom") {
        customAperture.style.display = 'inline-block';
        customApertureLabel.style.display = 'inline-block';;
    } else {
        customAperture.style.display = 'none';
        customApertureLabel.style.display = 'none';
    }
    // Recalculate q range
    SASCALC(instrument);
}

/*
 * Change the instrument you want to calculate Q ranges for
 */
function changeInstrument(domName, selectStr) {
    var inst = document.getElementById(domName);
    var instrumentOptions = [];
    for (var i = 0; i < inst.options.length; i++) {
        instrumentOptions.push(inst.options[i].value);
    }
    var instruments = {};
    var instName = "";
    for (var j in instrumentOptions) {
        instName = instrumentOptions[j]
        if (!(instName === "")) {
            instruments[instName] = document.getElementById(instName);
        }
    }
    for (var key in instruments) {
        if (key === selectStr) {
            instruments[key].style.display = "block";
        } else {
            instruments[key].style.display = "none";
        }
    }
    sessionStorage.setItem('instrument', selectStr);
    SASCALC(selectStr);
};


/*
 * Update the 1D Chart with new data sets
 */
function update1DChart(chartElement, xAxis, yDataSets, dataOptions) {
    var chart = new Chart(chartElement, {
        type: 'line',
        data: {
            labels: xAxis,
            datasets: yDataSets
        },
        options: dataOptions
    });
}

/*
 * Restore the persistant state on refresh
 */
function restorePersistantState() {
    // TODO: Update values on screen when values are loaded
    var instrument = sessionStorage.getItem('instrument');
    var instSelector = document.getElementById('instrumentSelector');
    instSelector.value = instrument;
    var ng7GuideConfig = sessionStorage.getItem('ng7GuideConfig');
    var ng7GuideSelector = document.getElementById('ng7GuideConfig');
    ng7GuideSelector.value = ng7GuideConfig;
    SASCALC(instrument);
}
