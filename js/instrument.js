const MAX_RPM = 5600;

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
        default:
            window.currentInstrument = null;
            break;
    }
    if (window.currentInstrument != null) {
        displayGeneralItems(instrument);
    }
}

function displayGeneralItems(instrument='', runSASCALC=false) {
    if (instrument) {
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
        setEventHandlers(instrument);
        // Run SASCALC
        if (runSASCALC) {
            window.currentInstrument.SASCALC();
        }
    }
}

function setAttributes(el, attrs) {
    for (var key in attrs) {
        el.setAttribute(key, attrs[key]);
    }
}

function createChildElement(parent, child, childType, childAttrs, childInnerHTML) {
    child = document.createElement(childType);
    setAttributes(child, childAttrs);
    child.innerHTML = childInnerHTML;
    parent.appendChild(child);
    return parent;
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
        // Initialize instrument object with default values
        this.loadDefaults();
        // Try to get values from the actual instrument
        this.getDeviceNodeMaps();
        // Use any values taken from the instrument
        this.useRealInstrumentValues();
        // Populate page using known values
        this.populatePageDynamically();
        // Create event handlers when changes are made
        this.setEventHandlers();
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
    useRealInstrumentValues() {
        throw new TypeError('The abstract useRealInstrumentValues() method must be implemented by Instrument sub-classes.');
    }

    /*
     * Generic method to point to all nodes on the page associated with the instrument
     * 
     * Standard SANS instruments (both 30m and 10m) should use this method.
     */
    populatePageDynamically() {
        // TODO: Rewrite this into a page generation function - Continue to point at nodes
        this.instrumentContainer = document.getElementById('instrument');
        if (this.instrumentContainer) {
            this.instrumentContainer.style.display = "block";
            // Remove all children before populating
            while (this.instrumentContainer.firstChild) {
                this.instrumentContainer.removeChild(this.instrumentContainer.lastChild);
            }
            // Create a sample table node if sample spaces are an option
            this.sampleTableContainer = null;
            this.sampleTableNode = null;
            if (this.sampleTableOptions) {
                var header, label;
                createChildElement(this.instrumentContainer, this.sampleTableContainer, 'div', { 'id': 'Sample' }, '');
                createChildElement(this.sampleTableContainer, header, 'h3', {}, 'Sample Space:');
                createChildElement(this.sampleTableContainer, label, 'label', { 'for': 'SampleTable' }, 'Sample Table: ');
                createChildElement(this.sampleTableContainer, this.sampleTableNode, 'select', { 'id': 'SampleTable' })
                for (sampleTable in Object.keys(this.sampleTableOptions)) {
                    var option;
                    createChildElement(this.sampleTableNode, option, 'option', { 'value': sampleTable }, sampleTable);
                    if (this.sampleTableDefault == sampleTable) {
                        option.selected = true;
                    }
                }
            }
            // Create a wavelength node if wavelength is an option
            this.wavelengthContainer = null;
            this.wavelengthNode = null;
            this.wavelengthSpreadNode = null;
            if (this.wavelengthOptions) {
                var header, label;
                createChildElement(this.instrumentNode, this.wavelengthContainer, 'div', { 'id': 'Wavelength' }, '');
                createChildElement(this.wavelengthContainer, header, 'h3', {}, 'Neutron Wavelength:');
                createChildElement(this.wavelengthContainer, label, 'label', { 'for': 'WavelengthInput' }, '&lambda; (&#8491;): ');
                // TODO: add limits based on selected wavelength spread - will need to do this after creating wavelength spread node
                createChildElement(this.wavelengthContainer, this.wavelengthNode, 'input', { 'type': 'number', 'value': this.wavelengthOptions.default, 'id': 'WavelengthInput' });
                var label;
                createChildElement(this.wavelengthContainer, label, 'label', { 'for': 'WavelengthSpread' }, '&Delta;&lambda;/&lambda; (%): ');
                createChildElement(this.wavelengthContainer, this.wavelengthSpreadNode, 'select', { 'id': 'WavelengthSpread' }, '');
                for (spreadValue in Object.keys(this.wavelengthOptions.spreads)) {
                    var option;
                    var spreadOptions = this.wavelengthOptions.spreads[spreadValue];
                    createChildElement(this.wavelengthSpreadNode, option, 'option', { 'value': str(spreadValue) }, spreadValue);
                }

                this.beamfluxNode = document.getElementById(this.instrumentName + 'BeamFlux');
                this.figureOfMeritNode = document.getElementById(this.instrumentName + 'FigureOfMerit');
                this.attenuatorNode = document.getElementById(this.instrumentName + 'Attenuators');
                this.attenuationFactorNode = document.getElementById(this.instrumentName + 'AttenuationFactor');
            } else {
                createChildElement(this.instrumentNode, this.wavelengthContainer, 'div', { 'id': 'Wavelength' }, '');
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

    setEventHandlers() {
        // Initialize oninput and onchange events for the given instrument
        // TODO: Move many of these functions inside the Instrument class
        this.sampleTableNode.onchange = function () { SASCALC(instrument); }
        this.wavelengthNode.onchange = function () { updateWavelength(instrument); }
        this.wavelengthSpreadNode.onchange = function () { updateWavelength(instrument); }
        this.guideConfigNode.onchange = function () { updateGuides(instrument, this.value); }
        this.sourceApertureNode.onchange = function () { SASCALC(instrument); }
        this.sampleApertureNode.onchange = function () { this.customApertureNode.value = this.value; updateAperture(instrument); }
        this.customApertureNode.onchange = function () { updateAperture(instrument); }
        this.sddSliderNode.onchange = function () { this.sddInputNode.value = this.value; SASCALC(instrument); }
        this.sddInputNode.oninput = function () { detectorSlider.value = this.value; SASCALC(instrument); }
        this.offsetSliderNode.onchange = function () { this.offsetInputNode.value = this.value; SASCALC(instrument); }
        this.offsetInputNode.oninput = function () { this.offsetSliderNode.value = this.value; SASCALC(instrument); }
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
     * Get the static and active device node maps from the instrument computer
     */
    async getDeviceNodeMaps() {
        try {
            if (this.isReal && this.hostname != '') {
                this.staticDeviceNodeMap = await connectToNice(callback = getStaticNodeMap, server = this.hostname);
                this.mutableDeviceNodeMap = await connectToNice(callback = getDevicesMap, server = this.hostname);
            }
            // TODO: Remove console output once node names are known and obvious
            for (nodeName in this.staticDeviceNodeMap) {
                console.log(nodeName + ": " + this.staticDeviceNodeMap[nodeName]);
            }
            for (nodeName in this.mutableDeviceNodeMap) {
                console.log(nodeName + ": " + this.mutableDeviceNodeMap[nodeName]);
            }
        } catch (err) {
            console.warn('Unable to connect to remote server: {$this.hostname}');
        }
    }

    SASCALC() {
        this.calculateInstrumentParameters()
        // Do Circular Average of an array of 1s
        calculateModel();
        // Update the charts
        update1DChart();
        update2DChart();
        // Set current configuration
        setCurrentConfig(this.instrumentName);
        // Store persistant state
        storePersistantState(this.instrumentName);
    }

    calculateInstrumentParameters() {
        // Calculate the beam stop diameter
        calculateBeamStopDiameter(this.instrumentName);
        // Calculate the estimated beam flux
        calculateBeamFlux(this.instrumentName);
        // Calculate the figure of merit
        calculateFigureOfMerit(this.instrumentName);
        // Calculate the number of attenuators
        calculateNumberOfAttenuators(this.instrumentName);
        // Do Circular Average of an array of 1s
        calculateQRangeSlicer(this.instrumentName);
        calculateMinimumAndMaximumQ(this.instrumentName);
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

    useRealInstrumentValues() {
        if (this.staticDeviceNodeMap) {
            var wavelengthSpreads = this.staticDeviceNodeMap['wavelengthSpread.wavelengthSpread']['permittedValues'];
            if (wavelengthSpreads && typeof wavelengthSpreads[Symbol.iterator] === 'function') {
                this.wavelengthOptions.spreads = {}
                for (var wavelengthSpread in wavelengthSpreads) {
                    var spread = wavelengthSpreads[wavelengthSpread];
                    var input = {
                        spread: {
                            // FIXME: Get real wavelength constants
                            constants: this.wavelengthOptions.spreads.spread.constants,
                            value: math.unit(float(spread), 'pct'),
                            range: [],}}
                    this.wavelengthOptions.spreads.push(input);
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
        if (this.mutableDeviceNodeMap) {
            // TODO: Use mutable values to populate page
        }
    }

    populatePageDynamically() {
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
}