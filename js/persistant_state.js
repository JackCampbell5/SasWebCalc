/*
 * Restore the persistant state on refresh
 */
function restorePersistantState() {
    var instrument = sessionStorage.getItem('instrument');
    if (instrument === "") {
        updateInstrument(instrument);
    }
    else if (instrument === "vsans") {
        restoreVSANSpersistantState();
    } else {
        // Load instrument and sample space
        var instSelector = document.getElementById('instrumentSelector');
        instSelector.value = instrument;
        updateInstrument(instrument, false);
        // Load model, model parameters, and averaging method and parameters
        var model = sessionStorage.getItem('model');
        var averageType = sessionStorage.getItem('averageType');
        var modelNode = document.getElementById('model');
        var averageTypeNode = document.getElementById('averagingType');
        modelNode.value = model;
        selectModel(model, false);
        modelParams = Object.keys(window.modelList[modelNode.value]['params']);
        for (var i = 0; i < modelParams.length; i++) {
            var paramName = model + "_" + modelParams[i];
            var paramNode = document.getElementById(paramName);
            paramNode.value = sessionStorage.getItem(paramName);
        }
        averageTypeNode.value = averageType;
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
        updateWavelength(instrument, false);
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
        // Restore frozen datasets
        window.frozenCalculations = JSON.parse(sessionStorage.getItem(instrument + 'FrozenDataSets'));
        window.frozenConfigs = JSON.parse(sessionStorage.getItem(instrument + 'FrozenConfigs'));
        window.currentConfig = JSON.parse(sessionStorage.getItem(instrument + 'CurrentConfig'));
        window.configNames = JSON.parse(sessionStorage.getItem(instrument + 'ConfigName'));
        if (window.frozenCalculations == "") {
            window.frozenCalculations = [];
        }
        if (window.frozenConfigs == "") {
            window.frozenConfigs = {};
        }
        if (window.currentConfig == "") {
            window.currentConfig = {};
        }
        if (window.configNames == "") {
            window.configNames = [];
        }
    }
    // Run SASCALC at the end
    SASCALC(instrument);
}

/*
 * Placeholder for the VSANS persistant state restore function
 * TODO: Actually write this
 */
function restoreVSANSpersistantState() {
    return;
}

/*
 * Store the persistant state for browser refreshes
 */
function storePersistantState(instrument) {
    // Store instrument and sample space
    sessionStorage.setItem('instrument', instrument);
    var sampleSelectStr = document.getElementById(instrument + 'SampleTable').value;
    sessionStorage.setItem(instrument + 'SampleTable', sampleSelectStr);
    // Store model, model parameters, and averaging method and parameters
    var modelNode = document.getElementById('model');
    var averageTypeNode = document.getElementById('averagingType');
    sessionStorage.setItem('model', modelNode.value);
    sessionStorage.setItem('averageType', averageTypeNode.value);
    defaultParams = Object.keys(window.modelList[modelNode.value]['params']);
    for (var i = 0; i < defaultParams.length; i++) {
        var paramName = modelNode.value + "_" + defaultParams[i];
        var paramNode = document.getElementById(paramName);
        var paramValue = paramNode.value;
        sessionStorage.setItem(paramName, paramValue);
    }
    // Store wavelength values
    var wavelength = document.getElementById(instrument + 'WavelengthInput');
    var wavelengthSpread = document.getElementById(instrument + 'WavelengthSpread');
    sessionStorage.setItem(instrument + 'WavelengthSpread', wavelengthSpread.value);
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
    // Store frozen datasets
    sessionStorage.setItem(instrument + 'FrozenDataSets', JSON.stringify(window.frozenCalculations));
    sessionStorage.setItem(instrument + 'FrozenConfigs', JSON.stringify(window.frozenConfigs));
    sessionStorage.setItem(instrument + 'CurrentConfig', JSON.stringify(window.currentConfig));
    sessionStorage.setItem(instrument + 'ConfigName', JSON.stringify(window.configNames));
}
