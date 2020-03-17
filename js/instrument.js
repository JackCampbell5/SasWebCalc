﻿const MAX_RPM = 5600;

function loadInstrumentClass() {
    var instrumentNode = document.getElementById('instrumentSelector');
    instrumentNode.onchange = function () {
        loadInstrument(this.value);
    }
}

function loadInstrument(instrument) {
    switch (instrument) {
        case 'ng7':
            window.currentInstrument = new NG7SANS();
            break;
    };
}


/*
 * Base pseudo-abstract class all instruments should derive from
 */
class Instrument {
    // IP or name of the server for NICE API connections
    static hostname = "";
    // Is the instrument a real peice of hardware?
    static isReal = false;
    // Unit of percent - used in wavelength spread values
    static percent = math.createUnit('percent', { definition: 1e-02, aliases: ['pct'] });

    constructor(instrumentName = "") {
        // DeviceNodeMaps as returned from the instrument - default to null
        this.staticDeviceNodeMap = null;
        this.mutableDeviceNodeMap = null;
        this.instrumentName = instrumentName;
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
        for (nodeName in this.staticDeviceNodeMap) {
            console.log(nodeName + ": " + this.staticDeviceNodeMap[nodeName]);
        }
        for (nodeName in this.mutableDeviceNodeMap) {
            console.log(nodeName + ": " + this.mutableDeviceNodeMap[nodeName]);
        }
    }
}


class NG7SANS extends Instrument {
    static instrumentName = "ng7";
    static hostname = "ng7sans.ncnr.nist.gov";
    static isReal = true;

    constructor() {
        super(NG7SANS.instrumentName);
    }
    
    loadDefaults() {
        // Sample space
        this.sampleTableDefault = "Chamber";
        this.sampleTableOptions = {
            "Chamber": { offset: math.unit(0, 'cm'), apertureOffset: math.unit(5.0, 'cm'), },
            "Huber": { offset: math.unit(54.8, 'cm'), apertureOffset: math.unit(5.0, 'cm'), },
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
                    value: math.unit(9.7, 'pct'),
                    range: [],
                },
                '13.9': {
                    constants: [16000, 0.950],
                    value: math.unit(13.9, 'pct'),
                    range: [],
                    defaultTilt: true,
                },
                '15.0': {
                    constants: [19000, 0.950],
                    value: math.unit(15.0, 'pct'),
                    range: [],
                },
                '25.7': {
                    constants: [25000, 1.6],
                    value: math.unit(25.7, 'pct'),
                    range: [],
                },
            },
        };
        // Neutron Optics
        this.collimation = {
            lengthMaximum: math.unit(1632, 'cm'),
            lengthPerUnit: math.unit(155, 'cm'),
            transmissionPerUnit: 0.974,
            width: math.unit(5.00, 'cm'),
            height: math.unit(5.00, 'cm'),
            gapAtStart: math.unit(188, 'cm'),
            options: {
                default: '0',
                apertureDefault: math.unit(1.43, 'cm'),
                '0': { name: '0 Guides', apertureOptions: [math.unit(1.43, 'cm'), math.unit(2.54, 'cm'), math.unit(3.81, 'cm')], },
                '1': { name: '1 Guide', apertureOptions: [math.unit(5.08, 'cm')], },
                '2': { name: '2 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                '3': { name: '3 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                '4': { name: '4 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                '5': { name: '5 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                '6': { name: '6 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                '7': { name: '7 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                '8': { name: '8 Guides', apertureOptions: [math.unit(5.08, 'cm')], },
                'LENS': { name: 'LENS', apertureOptions: [math.unit(1.43, 'cm')], },
            },
        };
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
        };
        // Beam stops
        this.beamstop = {
            1: { size: math.unit(1.0, 'inch'), distanceFromDetector: math.unit(0.0, 'cm'), },
            2: { size: math.unit(2.0, 'inch'), distanceFromDetector: math.unit(0.0, 'cm'), },
            3: { size: math.unit(3.0, 'inch'), distanceFromDetector: math.unit(0.0, 'cm'), },
            4: { size: math.unit(4.0, 'inch'), distanceFromDetector: math.unit(0.0, 'cm'), },
        };
        this.bsFactor = 1.05;
        // Flux constants
        this.flux = {
            perPixelMax: math.unit(100, 'Hz'),
            trans1: 0.63,
            trans2: 0.70,
            trans3: 0.75,
            b: 0.0395,
            c: 0.0442,
            peakFlux: math.unit(2.55e15, 'Hz'),
            peakWavelength: math.unit(5.0, 'angstrom'),
        };
        this.attenuation = {
            thickness: [math.unit(0.125, 'inch'), math.unit(0.250, 'inch'), math.unit(0.375, 'inch'), math.unit(0.500, 'inch'), math.unit(0.625, 'inch'), math.unit(0.750, 'inch'), math.unit(1.00, 'inch'), math.unit(1.25, 'inch'), math.unit(1.50, 'inch'), math.unit(1.75, 'inch')],
            factors: [0.498, 0.0792, 1.66e-3],
        };
    }

    populatePageDynamically() {
        // Available wavelength spreads
        if (this.staticDeviceNodeMap != null) {
            var wavelengthSpreads = this.staticDeviceNodeMap['wavelengthSpread.wavelengthSpread']['permittedValues'];
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
            // TODO: Populate GUIDES, SOURCE APERTURES, and DETECTOR LIMITS
            var sourceApertures = this.staticDeviceNodeMap['guide.sourceAperture']['permittedValues'];
            if (length(sourceApertures) > 0) {
                // Clear the options for source apertures
                this.sourceApertureOptions = {};
            }
            for (var aperture in sourceApertures) {
                var sourceAp = sourceApertures[aperture];
                this.sourceApertureOptions[sourceAp] = sourceAp + " cm";
            }
            var sourceAperturesGuide01 = this.staticDeviceNodeMap['guide01.key']['permittedValues'];
            var sourceAperturesGuide02 = this.staticDeviceNodeMap['guide02.key']['permittedValues'];
            var sourceAperturesGuide03 = this.staticDeviceNodeMap['guide03.key']['permittedValues'];
            var sourceAperturesGuide04 = this.staticDeviceNodeMap['guide04.key']['permittedValues'];
            var sourceAperturesGuide05 = this.staticDeviceNodeMap['guide05.key']['permittedValues'];
            var sourceAperturesGuide06 = this.staticDeviceNodeMap['guide06.key']['permittedValues'];
            var sourceAperturesGuide07 = this.staticDeviceNodeMap['guide07.key']['permittedValues'];
            var sourceAperturesGuide08 = this.staticDeviceNodeMap['guide08.key']['permittedValues'];
            var sourceAperturesGuide09 = this.staticDeviceNodeMap['guide09.key']['permittedValues'];
            var sourceAperturesGuide10 = this.staticDeviceNodeMap['guide10.key']['permittedValues'];
        }
        for (spread in this.wavelengthOptions.spreads) {
            var constants = this.wavelengthOptions.spreads[spread].constants;
            var min = (constants[1] + constants[0] / this.wavelengthOptions.max_rpm < this.wavelengthOptions.minimum) ? this.wavelengthOptions.minimum : math.unit(constants[1] + constants[0] / this.wavelengthOptions.max_rpm, 'angstrom');
            this.wavelengthOptions.spreads[spread].constants = [min, this.wavelengthOptions.maximum];
        }

    }
}