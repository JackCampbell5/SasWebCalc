/*
 * Restore the persistant state on refresh
 */
function restorePersistantState() {
    // Load instrument and sample space
    var instrument = sessionStorage.getItem('instrument');
    if (instrument === "") {
        return;
    } else if (instrument === "vsans") {
        restoreVSANSpersistantState();
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
        // Restore frozen datasets
        window.frozenCalculations = sessionStorage.getItem(instrument + 'FrozenDataSets');
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
    // Store frozen datasets
    sessionStorage.setItem(instrument + 'FrozenDataSets', window.frozenCalculations);
}
