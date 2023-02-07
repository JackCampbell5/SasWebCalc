//Is the first file to run when the page is loaded
function loadpage() {
    // Initialize data sets
    initializeData();
    clearFrozen(false);
    // Define base event handlers

    //When page is loaded - checks if dropdown changes
    var instrumentNode = document.getElementById('instrumentSelector');
    instrumentNode.onchange = function () {
        updateInstrumentNoInstrument();
    }
    var modelNode = document.getElementById('model');
    modelNode.onchange = function () {
        selectModel(this.value);
    }
    //# TODO move function to main
    populateModelSelector(modelNode);
    var averagingNode = document.getElementById('averagingType');
    averagingNode.onchange = function () {
        selectAveragingMethod(this.value);
    }
    // Restore persistent state on refresh
    restorePersistantState();
}

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
async function SASCALC(instrument) {
    // Initialize data sets - KEEP 12/6
    initializeData();

    console.log("Sas Calc Ran")

    await sendToPythonInstrument(instrument);
    console.log("sendToPythonInstrument ran")

    // Do Circular Average of an array of 1s
    await calculateModel();
    // Update the charts
    update1DChart();
    update2DChart();
    // Store persistant state
    storePersistantState(instrument);
    console.log("Sas Calc Finished")
    //NOTES     It works here and can change the value

}


/*
 * Change the instrument you want to calculate Q ranges for
 */
function updateInstrumentNoInstrument(runSASCALC = true) {
    //Finds the instrument
    var instrument = document.getElementById('instrumentSelector').value;
    updateInstrument(instrument, runSASCALC);
}
/*
 * Change the instrument you want to calculate Q ranges for
 * NEED for python
 */
function updateInstrument(instrument, runSASCALC=true) {
    // Get instrument node and create an array of the options available from original dropdown
    var inst = document.getElementById('instrumentSelector');
    var instrumentOptions = []; //Array of names of all the instruments
    for (var i = 0; i < inst.options.length; i++) {
        instrumentOptions.push(inst.options[i].value);
    }
    var instruments = {}; //Array for all of the instrument divs
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
    //If the instrument exists populate fields
    if (instrument != '' && instrument != null) {
        var serverNameNode = document.getElementById('serverName');
        serverNameNode.value = window[instrument + "Constants"]['serverName'];
        //Buttone above chats
        var buttons = document.getElementById('buttons');
        buttons.style.display = "inline-block";
        //TODO J     Figure out what all of this does
        var model = document.getElementById("model");
        model.style.display = "inline-block";
        selectModel(model.value, false);
        //Define Model types and label and make visible
        var modelLabel = document.getElementById("modelLabel");
        modelLabel.style.display = "inline-block";
        var modelParams = document.getElementById("modelParams");
        modelParams.style.display = "inline-block";
        //Define average method
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
 * Set the event handlers for the current active instrument
 */
function setEventHandlers(instrument) {
    // Initialize oninput and onchange events for the given instrument
    var sampleTableNode = document.getElementById(instrument + 'SampleTable');
    sampleTableNode.onchange = function () { SASCALC(instrument); }
    var wavelengthNode = document.getElementById(instrument + 'WavelengthInput');
    wavelengthNode.onchange = function () { SASCALC(instrument); }
    var wavelengthSpreadNode = document.getElementById(instrument + 'WavelengthSpread');
    wavelengthSpreadNode.onchange = function () { SASCALC(instrument); }
    var guideConfigNode = document.getElementById(instrument + 'GuideConfig');
    guideConfigNode.onchange = function () { updateGuides(instrument,this.value); }
    var apertureSourceNode = document.getElementById(instrument + 'SourceAperture');
    apertureSourceNode.onchange = function () { SASCALC(instrument); }
    var apertureSampleNode = document.getElementById(instrument + 'SampleAperture');
    apertureSampleNode.onchange = function () { SASCALC(instrument); }
    var apertureSampleCustomNode = document.getElementById(instrument + 'CustomAperture');
    apertureSampleCustomNode.onchange = function () { SASCALC(instrument); }
    var detectorSlider = document.getElementById(instrument + "SDDSliderBar");
    detectorSlider.onchange = function () {  detectorOutput.value = this.value; SASCALC(instrument);}
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
    //var send_button = document.getElementById('sendToNICE');
    //send_button.onclick = async function () { connectToNice(sendConfigsToNice); }
}
/*
 * Attempt to populate the page using values taken directly from the instrument
 * Any failed connections will cause the page to use the default values for all inputs
 */
async function populatePageDynamically(instrument) {
    //var staticNodeMap = await connectToNice(getStaticNodeMap);
    //var deviceMap = await connectToNice(getDevicesMap);
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
    //Question      Why is the below deprecated?
    var sourceApertures = staticNodeMap['guide.sourceAperture']['permittedValues'];
    var sourceAperturesGuide1 = staticNodeMap['guide01.key']['permittedValues'];
}
/*
 * Update the page when a new averaging method is selected
 * Need for python
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
   * Creates guide array for guide parameters
   * For pass to python method
 */
    function getGuideArray(instrument,whatReturn){
        var number_of_guides = 0;
        var lenses = false;
        const temp = document.getElementById(instrument + 'GuideConfig').value;
    if (temp === "LENS"){
        lenses = true;
        number_of_guides = 0;
    }else {
        number_of_guides = parseInt(temp);
    }
    if(whatReturn){return number_of_guides} else{return  lenses}
    }//End getGuideArray


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
function getCurrentConfig(instrument) {
//Deprecated function
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

async function sendToPythonInstrument(instrument) {
    // TODO: Gather all instrumental params here and pass them to the python (ignore return value for now)
    var json_object = {};
    json_object['instrument'] = instrument;
    json_object["wavelength"] = {}
    json_object["wavelength"]["wavelength"] = getWavelength(instrument);
    json_object['wavelength"]["wavelength_unit'] = window.units["wavelength"];
    json_object["wavelength"]["wavelength_spread"] = getWavelengthSpread(instrument) / 100;
    json_object["wavelength"]["wavelength_spread_unit"] = "Percent";
    json_object["wavelength"]["number_of_attenuators"] = getAttenuators(instrument);
    json_object["wavelength"]["attenuation_factor"] = 0.00021 //TODO FIX ME
        //document.getElementById(instrument + "Attenuators");
    //Makes 3 Python Dictionary as the collimation has 2 sub objects (source_aperture and sample_aperture) and a main object
    json_object["collimation"] = {};
    json_object["collimation"]["source_aperture"] = {};
    json_object["collimation"]["source_aperture"]["diameter"] = getSourceAperture(instrument);
    json_object["collimation"]["source_aperture"]["diameter_unit"] = window.units["source_aperture"];
    json_object["collimation"]["sample_aperture"] = {};
    json_object["collimation"]["sample_aperture"]["diameter"] = getSampleApertureSize(instrument);// TODO: Inst this supposed to be in inches?
    json_object["collimation"]["sample_aperture"]["diameter_unit"] = window.units["sampleAperture"];
    json_object["collimation"][0] = {};
    json_object["collimation"][0]["ssd"] = document.getElementById(instrument + 'SDD').value = " " ? 0.0 : document.getElementById(instrument + 'SDD').value ;
    json_object["collimation"][0]["ssd_unit"] = window.units["detectorDistance"];
    json_object["collimation"][0]["ssad"] = document.getElementById(instrument + 'SDD').value - window[instrument + "Constants"]['ApertureOffset'];
    json_object["collimation"][0]["ssad_unit"] = window.units["detectorDistance"];
    json_object["collimation"][0]["sample_space"] = document.getElementById(instrument + 'SampleTable').value;
    json_object["collimation"][0]["detector_distance"] = parseFloat(document.getElementById(instrument + 'SDDInputBox').value);
    json_object["collimation"]["guides"] = {};
    json_object["collimation"]["guides"]["number_of_guides"] = getGuideArray(instrument, true);
    json_object["collimation"]["guides"]["lenses"] = getGuideArray(instrument, false);
    //Some Instruments have more than one detector
    json_object["detectors"] = [];
    json_object["detectors"][0] = {};
    json_object["detectors"][0]["sdd"] = document.getElementById(instrument + 'SDD').value
    json_object["detectors"][0]["sdd_unit"] = window.units["detectorDistance"];
    json_object["detectors"][0]["offset"] = document.getElementById(instrument + "OffsetInputBox").value;
    json_object["detectors"][0]["offset_unit"] = window.units["detectorOffset"];
    json_object["detectors"][0]["pixel_size_x"] = window[instrument + "Constants"]["aPixel"];
    json_object["detectors"][0]["pixel_size_x_unit"] = 'mm';
    json_object["detectors"][0]["pixel_size_y"] = window[instrument + "Constants"]["aPixel"];
    json_object["detectors"][0]["pixel_size_y_unit"] = 'mm';
    json_object["detectors"][0]["pixel_no_x"] = window[instrument + "Constants"]["xPixels"].value;
    json_object["detectors"][0]["pixel_no_y"] = window[instrument + "Constants"]["yPixels"].value;
    json_object["beamStops"] = {};
    json_object["beamStops"]["diameter"] = document.getElementById(instrument + "BeamSize").value;
    json_object["beamStops"]["diameter_unit"] = window.units["beamDiameter"];
    json_object["beamStops"]["stop_size"] = document.getElementById(instrument + "BeamStopSize").value;
    json_object["beamStops"]["stop_diameter"] = window.units["beamStopDiameter"];
    json_object["slicer"] = {};
    json_object["slicer"]["averaging_params"] = getAveragingParams()
    json_object["average_type"] = document.getElementById("averagingType").value;


    // TODO: This will eventually need to be an asynchronous method and this call will need to wait for and capture the return
    const pythonDataEncoded = await post_data(`/calculate_instrument/${instrument}`, json_object);
    const pythonData = JSON.parse(pythonDataEncoded);

    var beamFluxNode = document.getElementById(instrument + 'BeamFlux');
    beamFluxNode.value = pythonData["user_inaccessible"]["beamFlux"];//Works
    const figureOfMeritNode = document.getElementById(instrument + 'FigureOfMerit');
    figureOfMeritNode.value = pythonData["user_inaccessible"]["figureOfMerit"]// Works
    const attenuatorNode = document.getElementById(instrument + "Attenuators");
    attenuatorNode.value = pythonData["user_inaccessible"]["numberOfAttenuators"]// Works
    const ssdNode = document.getElementById(instrument + "SSD");
    ssdNode.value = pythonData["user_inaccessible"]["ssd"] // Works
    const sddNode = document.getElementById(instrument + 'SDD')
    sddNode.value = pythonData["user_inaccessible"]["sdd"] // Works
    const beamStopNode = document.getElementById(instrument + "BeamSize")
    beamStopNode.value = pythonData["user_inaccessible"]["beamDiameter"] //Works
    const beamStopDiamNode  = document.getElementById(instrument+ "BeamStopSize")
    beamStopDiamNode.value = pythonData["user_inaccessible"]["beamStopDiameter"] // Works
    const attenuationFactorNode  = document.getElementById(instrument+ "AttenuationFactor")
    attenuationFactorNode.value = pythonData["user_inaccessible"]["attenuationFactor"] //Works

    const maxVertNode = document.getElementById(instrument + "MaximumVerticalQ");
    maxVertNode.value = pythonData["MaximumVerticalQ"]//CAN UPDATE
    maxHozNode = document.getElementById(instrument + "MaximumHorizontalQ");
    maxHozNode.value =  pythonData["MaximumHorizontalQ"]//CAN UPDATE
    var qMaxNode = document.getElementById(instrument + "MaximumQ");
    qMaxNode.value = pythonData["MaximumQ"]//Can Update
    var qMinNode = document.getElementById(instrument + "MinimumQ");
    qMinNode.value = pythonData["MinimumQ"]//Can Update
    window.nCells =pythonData["nCells"]
    window.dSQ =pythonData["qsq"]
    window.sigmaAve =pythonData["sigmaAve"]
    window.qAverage =pythonData["qAverage"]
    window.sigmaQ =pythonData["sigmaQ"]
    window.fSubs =pythonData["fSubs"]
    window.qxValues =pythonData["qxValues"]
    window.qyValues =pythonData["qyValues"]
    window.intensity2D = pythonData["intensitys2D"]
    window.qValues = pythonData["qValues"]
    const slicerReturnArray = pythonData["slicer_params"];
    const averageType = slicerReturnArray["averageType"];
    switch (averageType) {
        case "circular":
        default:
            window.slicer = new Circular(slicerReturnArray);
            break;
        case "sector":
            window.slicer = new Sector(slicerReturnArray);
            break;
        case "rectangular":
            window.slicer = new Rectangular(slicerReturnArray);
            break;
        case "elliptical":
            window.slicer = new Elliptical(slicerReturnArray);
            break;
    }//Averaging type switch end
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
