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
        window.frozenCalculations = sessionStorage.getItem(instrument + 'FrozenDataSets');
        window.frozenConfigs = sessionStorage.getItem(instrument + 'FrozenConfigs');
        window.currentConfig = sessionStorage.getItem(instrument + 'CurrentConfig');
        if (window.frozenCalculations == "") {
            window.frozenCalculations = [];
        }
        if (window.frozenConfigs == "") {
            window.frozenConfigs = {};
        }
        if (window.currentConfig == "") {
            window.currentConfig = {};
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
    var sampleSpaceNode = document.getElementById(instrument + 'SampleTable');
    var sampleSelectStr = sampleSpaceNode.options[sampleSpaceNode.selectedIndex].value;
    sessionStorage.setItem(instrument + 'SampleTable', sampleSelectStr);
    // Store model, model parameters, and averaging method and parameters
    var modelNode = document.getElementById('model');
    var averageTypeNode = document.getElementById('averagingType');
    sessionStorage.setItem('model', modelNode.value);
    sessionStorage.setItem('averageType', averageTypeNode.value);
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
    sessionStorage.setItem(instrument + 'FrozenDataSets', window.frozenCalculations);
    sessionStorage.setItem(instrument + 'FrozenConfigs', window.frozenConfigs);
    sessionStorage.setItem(instrument + 'CurrentConfig', window.currentConfig);
}
