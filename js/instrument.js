const MAX_RPM = 5600;


/*
 * Base pseudo-abstract class all instruments should derive from
 */
class Instrument {
    static instrumentName = "";
    static hostname = "";
    static isReal = false;
    static percent = math.createUnit('percent', { definition: 1e-02, aliases: ['%', 'pct'] });

    constructor() {
        this.loadDefaults();
        this.createNodeMap();
        this.populatePageDynamically();
    }

    /*
    * Pseudo-abstract method that populates the information on the page based off of information from the server
    */
    populatePageDynamically() {
        throw new TypeError('The abstract populatePageDynamically() method must be implemented by Instrument sub-classes.');
    }

    /*
     * Psuedo-abstract method to create constants associated with the instrument
     */
    loadDefaults() {
        throw new TypeError('The abstract loadDefaults() method must be implemented by Instrument sub-classes.');
    }

    /*
     * Generic method to point to all nodes on the page associated with the instrument
     * 
     * Standard SANS instruments (both 30m and 10m) should use this method. 
     */
    createNodeMap() {
        this.instrumentContainer = document.getElementById(this.instrumentName);
        if (this.instrumentContainer != null) {
            this.sampleTableContainer = document.getElementById(this.instrumentName + 'Sample');
            if (this.sampleTableContainer != null) {
                this.sampleTableNode = document.getElementById(this.instrumentName + 'SampleTable');
            }
            this.wavelengthContainer = document.getElementById(this.instrumentName + 'Wavelength');
            if (this.wavelengthContainer != null) {
                this.wavelengthNode = document.getElementById(this.instrumentName + 'WavelengthInput');
                this.wavelengthSpreadNode = document.getElementById(this.instrumentName + 'WavelengthSpread');
                this.beamfluxNode = document.getElementById(this.instrumentName + 'BeamFlux');
                this.figureOfMeritNode = document.getElementById(this.instrumentName + 'FigureOfMerit');
                this.attenuatorNode = document.getElementById(this.instrumentName + 'Attenuators');
                this.attenuationFactorNode = document.getElementById(this.instrumentName + 'AttenuationFactor');
            }
            this.collimationContainer = document.getElementById(this.instrumentName + 'Collimation');
            if (this.collimationContainer != null) {
                this.guideConfigNode = document.getElementById(this.instrumentName + 'GuideConfig');
                this.sourceApNode = document.getElementById(this.instrumentName + 'SourceAperture');
                this.sampleApNode = document.getElementById(this.instrumentName + 'SampleAperture');
                this.customApNode = document.getElementById(this.instrumentName + 'CustomAperture');
                this.ssdNode = document.getElementById(this.instrumentName + 'SSD');
            }
            this.detectorContainer = document.getElementById(this.instrumentName + 'Detector');
            if (this.detectorContainer != null) {
                this.sddInputNode = document.getElementById(this.instrumentName + 'SDDInputBox');
                this.sddSliderNode = document.getElementById(this.instrumentName + 'SDDSliderBar');
                this.sddDefaultsNode = document.getElementById(this.instrumentName + 'SDDDefaults');
                this.offsetInputNode = document.getElementById(this.instrumentName + 'OffsetInputBox');
                this.offsetSliderNode = document.getElementById(this.instrumentName + 'OffsetSliderBar');
                this.offsetDefaultsNode = document.getElementById(this.instrumentName + 'OffsetDefaults');
                this.sddNode = document.getElementById(this.instrumentName + 'SDD');
                this.beamSizeNode = document.getElementById(this.instrumentName + 'BeamSize');
                this.beamStopSizeNode = document.getElementById(this.instrumentName + 'BeamStopSize');
            }
            this.qRangeContainer = document.getElementById(this.instrumentName + 'QRange');
            if (this.qRangeContainer != null) {
                this.qMinNode = document.getElementById(this.instrumentName + 'MinimumQ');
                this.qMaxNode = document.getElementById(this.instrumentName + 'MaximumQ');
                this.qMaxVNode = document.getElementById(this.instrumentName + 'MaximumVerticalQ');
                this.qMaxHNode = document.getElementById(this.instrumentName + 'MaximumHorizontalQ');
            }
        } else {
            throw new TypeError(`Unknown instrument name: {$this.instrumentName}`);
        }
    }

    /*
     * Get the static and active device node maps from the instrument computer
     */
    async getDeviceNodeMaps() {
        var staticDeviceNodeMap = null;
        var mutableDeviceNodeMap = null;
        if (this.isReal && this.hostname != '') {
            staticDeviceNodeMap = await connectToNice(callback = getStaticNodeMap, server = this.hostname);
            mutableDeviceNodeMap = await connectToNice(callback = getDevicesMap, server = this.hostname);
        }
        return [staticDeviceNodeMap, mutableDeviceNodeMap];
    }
}


class NG7SANS extends Instrument {
    static instrumentName = "ng7";
    static hostname = "ng7sans.ncnr.nist.gov";
    static isReal = true;
    
    loadDefaults() {
        // Sample space
        this.sampleTableDefault = "Chamber";
        this.sampleTableOptions = ["Chamber", "Huber"];
        this.sampleToSDDOffsets = [math.unit(0, 'cm'), math.unit(54.8, 'cm')];

        this.wavelengthMin = math.unit(4.0, 'angstrom');
        this.wavelengthMax = math.unit(20.0, 'angstrom');
        this.wavelengthDefault = math.unit(6.0, 'angstrom');
        this.wavelengthSpreadOptions = [math.unit(9.7, '%'), math.unit(11.5, '%'), math.unit(13.9, '%'), math.unit(22.1, '%')];
        this.wavelengthSpreadDefault = math.unit(13.9, '%');
        this.wavelengthConstants = { '9.7': [13000, 0.560] }; // TODO: finish...
        this.wavelengthRange = {};
        for (spread in this.wavelengthSpreadOptions) {
            var constants = this.wavelengthConstants.spread;
            var min = (constants[1] + constants[0] / MAX_RPM < 4.0) ? this.wavelengthMin : math.unit(constants[1] + constants[0] / MAX_RPM, 'angstrom');
            this.wavelengthRange[spread] = [min, this.wavelengthMax];
        }

        this.guideOptions = { '0': '0 Guides', '1': '1 Guide', '2': '2 Guides', '3': '3 Guides', '4': '4 Guides', '5': '5 Guides', '6': '6 Guides', '7': '7 Guides', '8': '8 Guides', 'LENS': 'LENS'};
        this.guideOptionsDefault = '0';
        this.sourceApertureOptions = { '1.43': '1.43 cm', '2.54': '2.54 cm', '3.81': '3.81 cm', '5.08': '5.08 cm' }; // TODO: Units...
        this.sourceAprtureDefault = '5.08';
        this.guideToSourceApertureMap = {
            '0': ['1.43', '2.54', '3.81'],
            '1': ['5.08'],
            '2': ['5.08'],
            '3': ['5.08'],
            '4': ['5.08'],
            '5': ['5.08'],
            '6': ['5.08'],
            '7': ['5.08'],
            '8': ['5.08'],
            'LENS': ['1.43'],
        }

        this.sddMin = math.unit(91, 'cm');
        this.sddMax = math.unit(1531, 'cm');
        this.sddDefault = math.unit(100, 'cm');
        // TODO: Finish...
    }

    async populatePageDynamically() {
        var nodeMaps = this.getDeviceNodeMaps();
        var staticNodeMap = nodeMaps[0];
        var deviceMap = nodeMaps[1];

        // Available wavelength spreads
        var wavelengthSpreads = staticNodeMap['wavelengthSpread.wavelengthSpread']['permittedValues'];
        if (wavelengthSpreads != null && typeof wavelengthSpreads[Symbol.iterator] === 'function') {
            while (this.wavelengthSpreadNode.lastChild) {
                this.wavelengthSpreadNode.removeChild(this.wavelengthSpreadNode.lastChild);
            }
            for (var wavelengthSpread in wavelengthSpreads) {
                var spread = wavelengthSpreads[wavelengthSpread];
                var option = document.createElement("OPTION");
                var val = Math.round(1000 * parseFloat(spread.val)) / 10;
                option.value = val;
                option.appendChild(document.createTextNode(val));
                this.wavelengthSpreadNode.appendChild(option);
            }
        }

        // TODO: Populate GUIDES, SOURCE APERTURES, and DETECTOR LIMITS (and wavelength limits?)
        var sourceApertures = staticNodeMap['guide.sourceAperture']['permittedValues'];
        if (length(sourceApertures) > 0) {
            // Clear the options for source apertures
            this.sourceApertureOptions = {};
        }
        for (var aperture in sourceApertures) {
            var sourceAp = sourceApertures[aperture];
            this.sourceApertureOptions[sourceAp] = sourceAp + " cm";
        }
        var sourceAperturesGuide01 = staticNodeMap['guide01.key']['permittedValues'];
        var sourceAperturesGuide02 = staticNodeMap['guide02.key']['permittedValues'];
        var sourceAperturesGuide03 = staticNodeMap['guide03.key']['permittedValues'];
        var sourceAperturesGuide04 = staticNodeMap['guide04.key']['permittedValues'];
        var sourceAperturesGuide05 = staticNodeMap['guide05.key']['permittedValues'];
        var sourceAperturesGuide06 = staticNodeMap['guide06.key']['permittedValues'];
        var sourceAperturesGuide07 = staticNodeMap['guide07.key']['permittedValues'];
        var sourceAperturesGuide08 = staticNodeMap['guide08.key']['permittedValues'];
        var sourceAperturesGuide09 = staticNodeMap['guide09.key']['permittedValues'];
        var sourceAperturesGuide10 = staticNodeMap['guide10.key']['permittedValues'];
    }
}