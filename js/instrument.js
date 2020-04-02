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

function createChildElement(parent, childType, childAttrs, childInnerHTML) {
    var child = document.createElement(childType);
    setAttributes(child, childAttrs);
    child.innerHTML = childInnerHTML;
    parent.appendChild(child);
    return child;
}

function createChildElementWithLabel(parent, childType, childAttrs, childInnerHTML, labelInnerHTML) {
    createChildElement(parent, 'label', { 'for': childAttrs['id'] }, labelInnerHTML);
    child = createChildElement(parent, childType, childAttrs, childInnerHTML);
    return child;
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
        // Model() object
        this.modelNode = document.getElementById('model');
        this.setModel();
        // Slicer() object
        this.slicerNode = document.getElementById('averagingType');
        this.setSlicer();
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
        // TODO: Add minimums and maximums
        this.instrumentContainer = document.getElementById('instrument');
        if (this.instrumentContainer) {
            this.instrumentContainer.style.display = "block";
            // Remove all children before populating
            while (this.instrumentContainer.firstChild) {
                this.instrumentContainer.removeChild(this.instrumentContainer.lastChild);
            }
            // Create a sample table node if sample spaces are an option
            if (this.sampleTableOptions) {
                this.sampleTableContainer = createChildElement(this.instrumentContainer, 'div', { 'id': 'Sample', 'class': "slidecontainer instrument-section" }, '');
                createChildElement(this.sampleTableContainer, 'h3', {}, 'Sample Space:');
                this.sampleTableNode = createChildElementWithLabel(this.sampleTableContainer, 'select', { 'id': 'SampleTable' }, '', 'Sample Table: ')
                for (var sampleTable in this.sampleTableOptions) {
                    var option = createChildElement(this.sampleTableNode, 'option', { 'value': sampleTable }, sampleTable);
                    if (this.sampleTableDefault == sampleTable) {
                        option.selected = true;
                    }
                }
            }
            // Create a wavelength node if wavelength is an option
            if (this.wavelengthOptions) {
                this.wavelengthContainer = createChildElement(this.instrumentContainer, 'div', { 'id': 'Wavelength', 'class': "slidecontainer instrument-section" }, '');
                createChildElement(this.wavelengthContainer, 'h3', {}, 'Neutron Wavelength:');
                this.wavelengthNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'WavelengthInput' }, this.wavelengthOptions.default.toNumber(), '&lambda; (&#8491;): ');
                this.wavelengthSpreadNode = createChildElementWithLabel(this.wavelengthContainer, 'select', { 'id': 'WavelengthSpread' }, '', '&Delta;&lambda;/&lambda; (%): ');
                for (var spreadValue in this.wavelengthOptions.spreads) {
                    createChildElement(this.wavelengthSpreadNode, 'option', { 'value': spreadValue.toString() }, spreadValue);
                }
                // TODO: add wavelength limits based on selected wavelength spread - will need to do this after creating wavelength spread node
                var spreadOptions = this.wavelengthOptions.spreads[spreadValue];

                this.beamfluxNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'BeamFlux' }, '', 'Beam Flux (n-cm<sup>-1</sup>-sec<sup>-1</sup>): ');
                this.beamfluxNode.disabled = true;
                this.figureOfMeritNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'FigureOfMerit' }, '', 'Figure of Merit: ');
                this.figureOfMeritNode.disabled = true;
                this.attenuatorNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'Attenuators' }, '', 'Attenuators: ');
                this.attenuatorNode.disabled = true;
                this.attenuationFactorNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'AttenuationFactor' }, '', 'AttenuationFactor: ');
                this.attenuationFactorNode.disabled = true;
            }
            // Create a collimationOptions node if collimationOptions is an option
            if (this.collimationOptions) {
                var apertureDict = [];
                this.collimationContainer = createChildElement(this.instrumentContainer, 'div', { 'id': 'Collimation', 'class': "slidecontainer instrument-section"}, '');
                createChildElement(this.collimationContainer, 'h3', { 'id': 'Collimation'}, 'Collimation Settings:');
                this.guideConfigNode = createChildElementWithLabel(this.collimationContainer, 'select', { 'id': 'GuideConfig' }, '', 'Guides: ');
                for (var guideOption in this.collimationOptions.options) {
                    var optionDict = this.collimationOptions.options[guideOption];
                    for (var aperture in optionDict.apertureOptions) {
                        var value = optionDict.apertureOptions[aperture];
                        if (!apertureDict.includes(value)) {
                            apertureDict.push(value);
                        }
                    }
                    var option = createChildElement(this.guideConfigNode, 'option', { 'value': guideOption }, optionDict.name);
                    if (guideOption == this.collimationOptions.guideDefault) {
                        option.selected = true;
                    }
                }
                this.sourceApertureNode = createChildElementWithLabel(this.collimationContainer, 'select', { 'id': 'SourceAperture' }, '', 'Source Aperture: ');
                for (var key in apertureDict) {
                    var aperture = apertureDict[key];
                    var option = createChildElement(this.sourceApertureNode, 'option', { 'value': aperture.toNumber() }, aperture.toString());
                    if (aperture == this.collimationOptions.apertureDefault) {
                        option.selected = true;
                    }
                }
                this.sampleApertureNode = createChildElementWithLabel(this.collimationContainer, 'input', { 'type': 'number', 'value': '12.7', 'id': 'SampleAperture' }, '', 'Sample Aperture (cm): ');
                this.ssdNode = createChildElementWithLabel(this.collimationContainer, 'input', { 'type': 'number', 'id': 'SSD' }, '', 'Source-to-Sample Distance (cm): ');
                this.ssdNode.disabled = true;
            }
            if (this.detectorOptions) {
                this.sddInputNodes = [];
                this.sddSliderNodes = [];
                this.offsetInputNodes = [];
                this.offsetSliderNodes = [];
                this.sddNodes = [];
                this.beamSizeNodes = [];
                this.beamStopSizeNodes = [];
                this.detectorContainer = createChildElement(this.instrumentContainer, 'div', { 'id': 'Detector', 'class': "slidecontainer instrument-section" }, '');
                createChildElement(this.detectorContainer, 'h3', {}, 'Detector Settings:');
                for (var i in this.detectorOptions) {
                    // Differentiate multiple detectors, but only if multiple exist
                    if (this.detectorOptions.length > 1) {
                        createChildElement(this.detectorContainer, 'h4', {}, 'Detector #' + i);
                    }
                    var index = this.detectorOptions.length > 1 ? i : '';
                    var detector = this.detectorOptions[i];
                    this.sddInputNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'SDDInputBox' + index, 'type': 'number' }, '', 'Detector'.concat(index, ' Distance (cm): ')));
                    this.sddSliderNodes.push(createChildElement(this.detectorContainer, 'range', { 'id': 'SDDSliderBar' + index, 'class': 'slider', 'list': 'SDDdefaults' + index }, ''));
                    // TODO: Populate range sliders defaults
                    createChildElement(this.detectorContainer, 'defaults', { 'id': 'SDDdefaults' + index }, '');
                    this.offsetInputNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'OffsetInputBox' + index, 'type': 'number' }, '', 'Detector'.concat(index, ' Offset (cm): ')));
                    this.offsetSliderNodes.push(createChildElement(this.detectorContainer, 'range', { 'id': 'OffsetSliderBar' + index, 'class': 'slider', 'list': 'OffsetDefaults' + index  }, ''));
                    createChildElement(this.detectorContainer, 'defaults', { 'id': 'OffsetDefaults' + index }, '');
                    this.sddNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'SDD' + index }, '', 'Sample-To-Detector'.concat(index, ' Distance (cm): ')));
                    this.sddNodes[i].disabled = true;
                    this.beamSizeNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'BeamSize' + index, 'type': 'number' }, '', 'Beam Diameter (cm): '));
                    this.beamSizeNodes[i].disabled = true;
                    this.beamStopSizeNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'BeamStopSize' + index, 'type': 'number' }, '', 'Beam Stop Size (cm): '));
                    this.beamStopSizeNodes[i].disabled = true;
                }
            }
            this.qRangeContainer = createChildElement(this.instrumentContainer, 'div', { 'id': 'QRange', 'class': "slidecontainer instrument-section" }, '');
            createChildElement(this.qRangeContainer, 'h3', {}, 'Q Range:');
            this.qMinNode = createChildElementWithLabel(this.qRangeContainer, 'input', { 'id': 'MinimumQ', 'type': 'number' }, '', 'Minimum Q (&#8491;<sup>-1</sup>): ');
            this.qMaxNode = createChildElementWithLabel(this.qRangeContainer, 'input', { 'id': 'MaximumQ', 'type': 'number' }, '', 'Maximum Q (&#8491;<sup>-1</sup>): ');
            this.qMaxVerticalNode = createChildElementWithLabel(this.qRangeContainer, 'input', { 'id': 'MaximumVerticalQ', 'type': 'number' }, '', 'Maximum Vertical Q (&#8491;<sup>-1</sup>): ');
            this.qMaxHorizontalNode = createChildElementWithLabel(this.qRangeContainer, 'input', { 'id': 'MaximumhorizontalQ', 'type': 'number' }, '', 'Maximum Horizontal Q (&#8491;<sup>-1</sup>): ');
            if (!this.qIsInput) {
                this.qMinNode.disabled = true;
                this.qMaxNode.disabled = true;
                this.qMaxVerticalNode.disabled = true;
                this.qMaxHorizontalNode.disabled = true;
            }
        } else {
            throw new TypeError(`Unknown instrument name: {$this.instrumentName}`);
        }
    }

    setEventHandlers() {
        // Initialize oninput and onchange events for the given instrument
        if (this.sampleTableNode) {
            this.sampleTableNode.onchange = function () { this.SASCALC(); }
        }
        if (this.wavelengthContainer) {
            this.wavelengthNode.onchange = function () { updateWavelength(instrument); }
            this.wavelengthSpreadNode.onchange = function () { updateWavelength(instrument); }
        }
        if (this.guideConfigNode) {
            this.guideConfigNode.onchange = function () { updateGuides(instrument, this.value); }
        }
        if (this.sourceApertureNode) {
            this.sourceApertureNode.onchange = function () { this.SASCALC(); }
        }
        if (this.sampleApertureNode) {
            this.sampleApertureNode.onchange = function () { this.customApertureNode.value = this.value; updateAperture(instrument); }
        }
        if (this.detectorContainer) {
            for (var index in this.detectorOptions) {
                this.sddSliderNodes[index].onchange = function () { this.sddInputNodes[index].value = this.value; this.SASCALC(); }
                this.sddInputNodes[index].oninput = function () { this.sddSliderNodes[index].value = this.value; this.SASCALC(); }
                this.offsetSliderNodes[index].onchange = function () { this.offsetInputNodes[index].value = this.value; this.SASCALC(); }
                this.offsetInputNodes[index].oninput = function () { this.offsetSliderNodes[index].value = this.value; this.SASCALC(); }
            }
        }
        if (this.qIsInput) {
            this.qMinNode.onchange = function () { this.SASCALC() }
            this.qMaxNode.onchange = function () { this.SASCALC() }
            this.qMaxHorizontalNode.onchange = function () { this.SASCALC() }
            this.qMaxVerticalNode.onchange = function () { this.SASCALC() }
        }
        // Initialize onclick events for freezing and clearing calculations
        this.freezeButton = document.getElementById("freezeButton");
        this.freezeButton.onclick = function () { freezeSASCALC(); }
        this.clearFrozenButton = document.getElementById("clearFrozenButton");
        this.clearFrozenButton.onclick = function () { clearFrozen(); }
        // Initialize routine when button is displayed:
        this.send_button = document.getElementById('sendToNICE');
        this.send_button.onclick = async function () { connectToNice(sendConfigsToNice); }
        // Update model and slicer when changed
        this.modelNode.onchange = function () { this.setModel(); selectModel(this.model); }
        this.slicerNode.onchange = function () { this.setSlicer(); calculateQRangeSlicer(); }
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

    setModel() {
        this.model = this.modelNode.value;
    }

    setSlicer() {
        this.slicerName = this.slicerNode.value;
        switch (this.slicerName) {
            case 'circular':
                this.slicer = new Circular({}, this);
            case 'sector':
                this.slicer = new Sector({}, this);
            case 'rectangular':
                this.slicer = new Rectangular({}, this);
            case 'annular':
                this.slicer = new Annular({}, this);
            case 'elliptical':
                this.slicer = new Elliptical({}, this);
        }
    }

    // TODO: Move all of these into the class
    SASCALC() {
        // Calculate any instrument parameters
        // Keep as a separate function so Q-range entries can ignore this
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
        this.collimationOptions = {
            lengthMaximum: math.unit(1632, 'cm'),
            lengthPerUnit: math.unit(155, 'cm'),
            transmissionPerUnit: 0.974,
            width: math.unit(5.00, 'cm'),
            height: math.unit(5.00, 'cm'),
            gapAtStart: math.unit(188, 'cm'),
            guideDefault: '0',
            apertureDefault: math.unit(1.43, 'cm'),
            options: {
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
        this.detectorOptions = [
            {
                name: "Ordela2D",
                pixels: {
                    xSize: math.unit(5.08, 'mm'),
                    ySize: math.unit(5.08, 'mm'),
                    dimensions: [128, 128],
                },
                range: [math.unit(91, 'cm'), math.unit(1531, 'cm')],
                default: math.unit(100, 'cm'),
                offsetRange: [math.unit(0, 'cm'), math.unit(25, 'cm')],
                offsetDefault: math.unit(0, 'cm'),
            },
        ];
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
            coeff: 10000,
            peakFlux: math.unit(2.55e15, 'Hz'),
            peakWavelength: math.unit(5.0, 'angstrom'),
        };
        this.attenuation = {
            thickness: [math.unit(0.125, 'inch'), math.unit(0.250, 'inch'), math.unit(0.375, 'inch'), math.unit(0.500, 'inch'), math.unit(0.625, 'inch'), math.unit(0.750, 'inch'), math.unit(1.00, 'inch'), math.unit(1.25, 'inch'), math.unit(1.50, 'inch'), math.unit(1.75, 'inch')],
            factors: [0.498, 0.0792, 1.66e-3],
        };
        this.qIsInput = false;
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
}