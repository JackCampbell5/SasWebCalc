const MAX_RPM = 5600;


/*
 * Base pseudo-abstract class all instruments should derive from
 */
class Instrument {
    // Name of the instrument
    static instrumentName = "";
    // IP or name of the server for NICE API connections
    static hostname = "";
    // Is the instrument a real peice of hardware?
    static isReal = false;
    // Unit of percent - used in wavelength spread values
    static percent = math.createUnit('percent', { definition: 1e-02, aliases: ['%', 'pct'] });

    constructor() {
        // DeviceNodeMaps as returned from the instrument - default to null
        this.staticDeviceNodeMap = null;
        this.mutableDeviceNodeMap = null;
        // Initialize instrument object
        this.loadDefaults();
        this.createPageNodeMap();
        this.getDeviceNodeMaps();
        this.populatePageDynamically();
    }

    /*
     * Psuedo-abstract method to initialize constants associated with an instrument
     */
    loadDefaults() {
        throw new TypeError('The abstract loadDefaults() method must be implemented by Instrument sub-classes.');
    }

    /*
    * Pseudo-abstract method that populates the information on the page based off of information from the server
    */
    populatePageDynamically() {
        throw new TypeError('The abstract populatePageDynamically() method must be implemented by Instrument sub-classes.');
    }

    /*
     * Generic method to point to all nodes on the page associated with the instrument
     * 
     * Standard SANS instruments (both 30m and 10m) should use this method.
     */
    createPageNodeMap() {
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
                this.sourceApertureNode = document.getElementById(this.instrumentName + 'SourceAperture');
                this.sampleApertureNode = document.getElementById(this.instrumentName + 'SampleAperture');
                this.customApertureNode = document.getElementById(this.instrumentName + 'CustomAperture');
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
                this.qMaxVerticalNode = document.getElementById(this.instrumentName + 'MaximumVerticalQ');
                this.qMaxHorizontalNode = document.getElementById(this.instrumentName + 'MaximumHorizontalQ');
            }
        } else {
            throw new TypeError(`Unknown instrument name: {$this.instrumentName}`);
        }
    }

    /*
     * Get the static and active device node maps from the instrument computer
     */
    async getDeviceNodeMaps() {
        try {
            if (this.isReal && this.hostname != '') {
                this.staticDeviceNodeMap = await connectToNice(callback = getStaticNodeMap, server = this.hostname);
                this.mutableDeviceNodeMap = await connectToNice(callback = getDevicesMap, server = this.hostname);
            }
        } catch (err) {
            console.warn('Unable to connect to remote server: {$this.hostname}');
        }
    }
}


class NG7SANS extends Instrument {
    static instrumentName = "ng7";
    static hostname = "ng7sans.ncnr.nist.gov";
    static isReal = true;
    
    loadDefaults() {
        // Sample space
        this.sampleTableDefault = "Chamber";
        this.sampleTableOptions = {
            "Chamber": { offset: math.unit(0, 'cm') },
            "Huber": { offset: math.unit(54.8, 'cm') }
        };
        // Wavelength
        this.wavelengthOptions = {
            name: "",
            default: math.unit(6.0, 'angstrom'),
            minimum: math.unit(4.0, 'angstrom'),
            maximum: math.unit(20.0, 'angstrom'),
            max_rpm: 5600,
            spreads: {
                '9.7': {
                    constants: [13000, 0.560],
                    value: math.unit(9.7, '%'),
                    range: [],
                },
                '13.9': {
                    constants: [16000, 0.950],
                    value: math.unit(13.9, '%'),
                    range: [],
                    defaultTilt: true,
                },
                '15.0': {
                    constants: [19000, 0.950],
                    value: math.unit(15.0, '%'),
                    range: [],
                },
                '25.7': {
                    constants: [25000, 1.6],
                    value: math.unit(25.7, '%'),
                    range: [],
                },
            },
        }
        // Neutron Optics
        // TODO: Larger dictionary including guide lengths, etc.
        this.guideOptions = { '0': '0 Guides', '1': '1 Guide', '2': '2 Guides', '3': '3 Guides', '4': '4 Guides', '5': '5 Guides', '6': '6 Guides', '7': '7 Guides', '8': '8 Guides', 'LENS': 'LENS'};
        this.guideOptionsDefault = '0';
        this.sourceApertureOptions = { '1.43': math.unit(1.43, 'cm'), '2.54': math.unit(2.54, 'cm'), '3.81': math.unit(3.81, 'cm'), '5.08': math.unit(5.08, 'cm') };
        this.sourceApertureDefault = '5.08';
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
        // Detectors
        this.detector = {
            "Ordela2D": {
                pixels: {
                    xSize: math.unit(5.08, 'mm'),
                    ySize: math.unit(5.08, 'mm'),
                    dimensions: [128, 128],
                },
                range: [math.unit(91, 'cm'), math.unit(1531, 'cm')],
                default: math.unit(100, 'cm'),
                offsetRange: [math.unit(0, 'cm'), math.unit(25, 'cm')],
                offsetDefault: math.unit(0, 'cm'),
            }
        }

        // TODO: Beamstops, flux, attenuators

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
        for (spread in this.wavelengthOptions.spreads) {
            var constants = spread.constants;
            var min = (constants[1] + constants[0] / this.wavelengthOptions.max_rpm < this.wavelengthOptions.minimum) ? this.wavelengthOptions.minimum : math.unit(constants[1] + constants[0] / this.wavelengthOptions.max_rpm, 'angstrom');
            this.wavelengthOptions[spread].constants = [min, this.wavelengthMax];
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