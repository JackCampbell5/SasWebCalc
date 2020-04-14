function loadInstrumentClass() {
    // Initialize data sets
    initializeData();
    var instrumentNode = document.getElementById('instrumentSelector');
    instrumentNode.onchange = function () {
        loadInstrument(this.value);
    }
    // Initialize onclick events for freezing and clearing calculations
    var freezeButton = document.getElementById("freezeButton");
    freezeButton.onclick = function () { freezeSASCALC(); }
    var clearFrozenButton = document.getElementById("clearFrozenButton");
    clearFrozenButton.onclick = function () { clearFrozen(); }
    // Initialize routine when button is displayed:
    var send_button = document.getElementById('sendToNICE');
    send_button.onclick = async function () { connectToNice(sendConfigsToNice); }
    // Update model and slicer when changed
    var modelNode = document.getElementById('model');
    modelNode.onchange = function () { window.currentInstrument.setModel(); selectModel(window.currentInstrument.model); }
    var slicerNode = document.getElementById('averagingType');
    slicerNode.onchange = function () { window.currentInstrument.setSlicer(); window.currentInstrument.calculateQRangeSlicer(); }
}

function loadInstrument(instrument) {
    // TODO: Calculation metrics - figure out why everything takes 3-5 seconds
    switch (instrument) {
        case 'ng7':
            window.currentInstrument = new NG7SANS();
            break;
        default:
            window.currentInstrument = null;
            break;
    }
    if (window.currentInstrument != null) {
        window.qxValues = [];
        window.qyValues = [];
        window.intensity2D = [];
        window.mask = [];
        displayGeneralItems(instrument);
        window.currentInstrument.SASCALC();
    }
}

function displayGeneralItems(instrument = null) {
    if (instrument) {
        if (instrument.isReal) {
            var serverNameNode = document.getElementById('serverName');
            serverNameNode.value = window.currentInstrument.hostname;
        }
        var buttons = document.getElementById('buttons');
        buttons.style.display = "inline-block";
        var model = document.getElementById("model");
        model.style.display = "inline-block";
        var modelLabel = document.getElementById("modelLabel");
        modelLabel.style.display = "inline-block";
        var modelParams = document.getElementById("modelParams");
        modelParams.style.display = "inline-block";
        var averagingType = document.getElementById("averagingType");
        averagingType.style.display = "inline-block";
        var averagingTypeLabel = document.getElementById("averagingTypeLabel");
        averagingTypeLabel.style.display = "inline-block";
        // Set Model() object
        window.currentInstrument.setModel(false);
        // Set Slicer() object
        window.currentInstrument.setSlicer();
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

function generateOnesArray(index = 0) {
    var xPixels = parseInt(window.currentInstrument.detectorOptions[index].pixels.dimensions[0]);
    var yPixels = parseInt(window.currentInstrument.detectorOptions[index].pixels.dimensions[1]);
    var data = new Array();
    var dataY = new Array();
    for (var i = 0; i < xPixels; i++) {
        let dataY = new Array(yPixels).fill(1);
        data[i] = dataY;
    }
    return data;
}

function generateStandardMaskArray(index = 0) {
    var xPixels = parseInt(window.currentInstrument.detectorOptions[index].pixels.dimensions[0]);
    var yPixels = parseInt(window.currentInstrument.detectorOptions[index].pixels.dimensions[1]);
    var mask = new Array();
    for (var i = 0; i < xPixels; i++) {
        var maskInset = new Array(yPixels).fill(0);
        for (var j = 0; j < yPixels; j++) {
            if ((i <= 1 || i >= xPixels - 2) ||(j <= 1 || j >= yPixels - 2)) {
                // Left and right two pixels should be masked
                maskInset[j] = 1;
            }
        }
        mask[i] = maskInset;
    }
    return mask;
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
        // Point to slicer and model nodes
        this.setSlicerName();
        this.setModelName();
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
     * Standard SANS instruments (both 30m and 10m) should use this method. VSANS Might be able to as well.
     */
    populatePageDynamically() {
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
                this.wavelengthNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'WavelengthInput', 'value': this.wavelengthOptions.default.toNumeric() }, '', '&lambda; (&#8491;): ');
                this.wavelengthSpreadNode = createChildElementWithLabel(this.wavelengthContainer, 'select', { 'id': 'WavelengthSpread' }, '', '&Delta;&lambda;/&lambda; (%): ');
                for (var spreadValue in this.wavelengthOptions.spreads) {
                    createChildElement(this.wavelengthSpreadNode, 'option', { 'value': spreadValue.toString() }, spreadValue);
                }
                this.calculateWavelengthRange();

                this.beamfluxNode = createChildElementWithLabel(this.wavelengthContainer, 'input', { 'type': 'number', 'id': 'BeamFlux' }, '', 'Beam Flux (n-cm<sup>-2</sup>-sec<sup>-1</sup>): ');
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
                        if (!math.compare(value, apertureDict).includes(0)) {
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
                this.sampleApertureNode = createChildElementWithLabel(this.collimationContainer, 'input', { 'type': 'number', 'value': '1.27', 'id': 'SampleAperture' }, '', 'Sample Aperture (cm): ');
                this.ssdNode = createChildElementWithLabel(this.collimationContainer, 'input', { 'type': 'number', 'id': 'SSD' }, '', 'Source-to-Sample Distance (cm): ');
                this.ssdNode.disabled = true;
                this.updateGuides(false);
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
                    this.sddInputNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'SDDInputBox' + index, 'type': 'number', 'min': detector.range[0].toNumeric(), 'max': detector.range[1].toNumeric(), 'value': detector.default.toNumeric() }, '', 'Detector'.concat(index, ' Distance (cm): ')));
                    this.sddSliderNodes.push(createChildElement(this.detectorContainer, 'input', { 'id': 'SDDSliderBar' + index, 'type': 'range', 'class': 'slider', 'list': 'sddDefaults' + index, 'min': detector.range[0].toNumeric(), 'max': detector.range[1].toNumeric(), 'value': detector.default.toNumeric() }, ''));
                    let datalist = createChildElement(this.detectorContainer, 'datalist', { 'id': 'sddDefaults' + index }, '');
                    for (var sliderIndex in detector.sliderDefaults) {
                        let item = detector.sliderDefaults[sliderIndex];
                        createChildElement(datalist, 'option', { 'value': item.toNumeric(), 'label': item.toNumeric() }, '');
                    }
                    this.offsetInputNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'OffsetInputBox' + index, 'type': 'number', 'min': detector.offsetRange[0].toNumeric(), 'max': detector.offsetRange[1].toNumeric(), 'value': detector.offsetDefault.toNumeric() }, '', 'Detector'.concat(index, ' Offset (cm): ')));
                    this.offsetSliderNodes.push(createChildElement(this.detectorContainer, 'input', { 'id': 'OffsetSliderBar' + index, 'type': 'range', 'class': 'slider', 'list': 'offsetDefaults' + index, 'min': detector.offsetRange[0].toNumeric(), 'max': detector.offsetRange[1].toNumeric(), 'value': detector.offsetDefault.toNumeric() }, ''));
                    let datalistOffset = createChildElement(this.detectorContainer, 'datalist', { 'id': 'offsetDefaults' + index }, '');
                    for (var sliderIndex in detector.offsetSliderDefaults) {
                        let item = detector.offsetSliderDefaults[sliderIndex];
                        createChildElement(datalistOffset, 'option', { 'value': item.toNumeric(), 'label': item.toNumeric() }, '');
                    }
                    this.sddNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'SDD' + index }, '', 'Sample-To-Detector'.concat(index, ' Distance (cm): ')));
                    this.sddNodes[i].disabled = true;
                    this.beamSizeNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'BeamSize' + index, 'type': 'number' }, '', 'Beam Diameter (cm): '));
                    this.beamSizeNodes[i].disabled = true;
                    this.beamStopSizeNodes.push(createChildElementWithLabel(this.detectorContainer, 'input', { 'id': 'BeamStopSize' + index, 'type': 'number' }, '', 'Beam Stop Size (inch): '));
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
            this.sampleTableNode.onchange = function () { window.currentInstrument.SASCALC(); }
        }
        if (this.wavelengthContainer) {
            this.wavelengthNode.onchange = function () { window.currentInstrument.updateWavelength(); }
            this.wavelengthSpreadNode.onchange = function () { window.currentInstrument.updateWavelength(); }
        }
        if (this.guideConfigNode) {
            this.guideConfigNode.onchange = function () { window.currentInstrument.updateGuides(); }
        }
        if (this.sourceApertureNode) {
            this.sourceApertureNode.onchange = function () { window.currentInstrument.SASCALC(); }
        }
        if (this.sampleApertureNode) {
            this.sampleApertureNode.onchange = function () {
                window.currentInstrument.sampleApertureNode.value = this.value;
                window.currentInstrument.SASCALC();
            }
        }
        if (this.detectorContainer) {
            for (var index in this.detectorOptions) {
                this.sddSliderNodes[index].onchange = function () {
                    window.currentInstrument.sddInputNodes[index].value = window.currentInstrument.sddSliderNodes[index].value;
                    window.currentInstrument.SASCALC();
                }
                this.sddInputNodes[index].oninput = function () {
                    window.currentInstrument.sddSliderNodes[index].value = window.currentInstrument.sddInputNodes[index].value;
                    window.currentInstrument.SASCALC();
                }
                this.offsetSliderNodes[index].onchange = function () {
                    window.currentInstrument.offsetInputNodes[index].value = window.currentInstrument.offsetSliderNodes[index].value;
                    window.currentInstrument.SASCALC();
                }
                this.offsetInputNodes[index].oninput = function () {
                    window.currentInstrument.offsetSliderNodes[index].value = window.currentInstrument.offsetInputNodes[index].value;
                    window.currentInstrument.SASCALC();
                }
            }
        }
        if (this.qIsInput) {
            this.qMinNode.onchange = function () { window.currentInstrument.SASCALC() }
            this.qMaxNode.onchange = function () { window.currentInstrument.SASCALC() }
            this.qMaxHorizontalNode.onchange = function () { window.currentInstrument.SASCALC() }
            this.qMaxVerticalNode.onchange = function () { window.currentInstrument.SASCALC() }
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

    setModelName() {
        this.modelNode = document.getElementById('model');
        this.model = this.modelNode.value;
    }
    setModel(runSasCalc = true) {
        this.setModelName()
        selectModel(this.model, runSasCalc);
    }
    setSlicerName() {
        this.slicerNode = document.getElementById('averagingType');
        this.slicerName = this.slicerNode.value;
    }
    setSlicer() {
        this.setSlicerName();
        slicerSelection(this.slicerName);
    }

    SASCALC() {
        // Calculate any instrument parameters
        // Keep as a separate function so Q-range entries can ignore this
        this.calculateInstrumentParameters();
        // Do average of an array of 1s
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
        this.calculateBeamStopDiameter();
        // Calculate the estimated beam flux
        this.calculateBeamFlux();
        // Calculate the figure of merit
        this.calculateFigureOfMerit();
        // Calculate the number of attenuators
        this.calculateAttenuators();
        // Do Circular Average of an array of 1s
        for (var index in this.detectorOptions) {
            this.calculateMinimumAndMaximumQ(index);
            this.calculateQRangeSlicer(index);
        }
    }

    calculateAttenuationFactor(index = 0) {
        var a2 = this.getSampleApertureSize();
        var beamDiam = this.getBeamDiameter(index);
        var aPixel = this.detectorOptions[index].pixels.xSize;
        var iPixelMax = this.flux.perPixelMax;
        var num_pixels = math.multiply(math.divide(math.PI, 4), math.pow(math.divide(math.multiply(0.5, math.add(a2, beamDiam)), aPixel), 2));
        var iPixel = math.divide(this.getBeamFlux(), num_pixels);
        var atten = (iPixel < iPixelMax) ? 1.0 : math.divide(iPixelMax, iPixel);
        this.attenuationFactorNode.value = (atten == 1.0) ? atten: atten.toNumeric();
    }
    calculateAttenuators() {
        this.calculateAttenuationFactor();
        var atten = this.getAttenuationFactor();
        var af = math.add(0.498, math.subtract(math.multiply(math.unit(0.0792, 'angstrom^-1'), this.getWavelength()), math.multiply(math.unit(1.66e-3, 'angstrom^-2'), math.pow(this.getWavelength(), 2))));
        var nf = math.multiply(-1, math.divide(math.log(atten), af));
        var numAtten = math.ceil(nf);
        if (numAtten > 6) {
            numAtten = 7 + Math.floor((numAtten - 6) / 2);
        }
        this.attenuatorNode.value = numAtten;
    }
    calculateBeamCenterX(index = 0) {
        // Find the number of x pixels in the detector
        var xPixels = this.detectorOptions[index].pixels.dimensions[0];
        // Get pixel size in mm and convert to cm
        var dr = this.detectorOptions[index].pixels.xSize;
        // Get detector offset in cm
        var offset = this.getDetectorOffset();
        var xCenter = math.add(math.divide(offset, dr), math.add(math.divide(xPixels, 2), 0.5));
        return xCenter;
    }
    calculateBeamDiameter(index = 0, direction = 'maximum') {
        // Update all instrument calculations needed for beam diameter
        this.calculateSourceToSampleApertureDistance();
        this.calculateSampleToDetectorDistance(index);
        // Get instrumental values
        var sourceAperture = this.getSourceApertureSize();
        var sampleAperture = this.getSampleApertureSize();
        var SSD = this.getSourceToSampleApertureDistance();
        var SDD = this.getSampleApertureToDetectorDistance(index);
        var wavelength = this.getWavelength();
        var wavelengthSpread = this.getWavelengthSpread();
        if (this.guideConfigNode.value === 'LENS') {
            // If LENS configuration, the beam size is the source aperture size
            // FIXME: This is showing -58 cm... Why?!?!
            this.beamSizeNodes[index].value = this.getSourceApertureSize().toNumeric();
        }
        // Calculate beam width on the detector
        var beamWidth = math.add(math.multiply(sourceAperture, math.divide(SDD, SSD)),
            math.divide(math.multiply(sampleAperture, math.add(SSD, SDD)), SSD));
        // Beam height due to gravity
        var bv3 = math.multiply(math.multiply(math.add(SSD, SDD), SDD), math.pow(wavelength, 2));
        var bv4 = math.multiply(bv3, wavelengthSpread);
        var bv = math.add(beamWidth, math.multiply(math.unit(0.0000125, 'percent^-1cm^-3'), bv4));
        // Larger of the width*safetyFactor and height
        var bm_bs = math.multiply(this.bsFactor, beamWidth);
        let bm = (bm_bs > bv) ? bm_bs : bv;
        var beamDiam;
        switch (direction) {
            case 'vertical':
                beamDiam = bv;
                break;
            case 'horizontal':
                beamDiam = bh;
                break;
            case 'maximum':
            default:
                beamDiam = bm;
        }
        this.beamSizeNodes[index].value = beamDiam.toNumeric();
    }
    calculateBeamStopDiameter(index = 0) {
        this.calculateBeamDiameter(index, 'maximum');
        this.beamStopSizeNodes[index].setAttribute('style', '');
        var beamDiam = this.getBeamDiameter(index);
        for (var i in this.beamstop) {
            var beamStopIDict = this.beamstop[i];
            if (math.compare(beamStopIDict.size, beamDiam) >= 0) {
                this.beamStopSizeNodes[index].value = beamStopIDict.size.toNumeric();
                return;
            }
        }
        // If this is reached, that means the beam diameter is larger than the largest known beamstop
        this.beamStopSizeNodes[index].value = beamStopIDict.size.toNumeric();
        this.beamStopSizeNodes[index].setAttribute('style', 'color:red');
    }
    calculateBeamStopProjection(index = 0) {
        this.calculateSampleToDetectorDistance(index);
        this.calculateBeamDiameter(index);
        this.calculateBeamStopDiameter(index);
        var bsDiam = this.getBeamStopDiameter(index);
        var sampleAperture = this.getSampleApertureSize();
        var L2 = this.getSampleApertureToDetectorDistance();
        var LBeamstop = math.add(math.unit(20.1, 'cm'), math.multiply(1.61, this.getBeamStopDiameter())); //distance in cm from beamstop to anode plane (empirical)
        return math.add(bsDiam, math.multiply(math.add(bsDiam, sampleAperture), math.divide(LBeamstop, math.subtract(L2, LBeamstop)))); // Return value is in cm
    }
    calculateBeamFlux() {
        // FIXME: Flux calculation is about 7x too high
        // Get constants
        var peakLambda = this.flux.peakWavelength;
        var peakFlux = this.flux.peakFlux;
        var guideGap = this.collimationOptions.gapAtStart;
        var guideLoss = this.collimationOptions.transmissionPerUnit;
        var guideWidth = this.collimationOptions.width;
        var trans1 = this.flux.trans1;
        var trans2 = this.flux.trans2;
        var trans3 = this.flux.trans3;
        var b = this.flux.b;
        var c = this.flux.c;
        var sourceAperture = this.getSourceApertureSize();
        var sampleAperture = this.getSampleApertureSize();
        var SDD = this.getSampleToDetectorDistance();
        var lambda = this.getWavelength();
        var lambdaSpread = this.getWavelengthSpread();
        var guides = this.getNumberOfGuides();

        // Run calculations
        var alpha = math.divide(math.add(sourceAperture, sampleAperture), math.multiply(2, SDD));
        var f = math.divide(math.multiply(guideGap, alpha), math.multiply(2, guideWidth));
        var trans4 = math.multiply(math.subtract(1, f), math.subtract(1, f));
        var trans5 = math.exp(math.multiply(guides, Math.log(guideLoss)));
        var trans6 = math.subtract(1, math.multiply(lambda, math.subtract(b, math.multiply(math.divide(guides, 8), math.subtract(b, c)))));
        var totalTrans = math.multiply(trans1, trans2, trans3, trans4, trans5, trans6);

        var area = math.chain(math.PI).multiply(sampleAperture.toNumeric()).multiply(sampleAperture.toNumeric()).divide(4).done();
        var d2_phi = math.divide(peakFlux, math.multiply(2, math.PI));
        d2_phi = math.multiply(d2_phi, math.exp(math.multiply(4, math.log(math.divide(peakLambda, lambda)))));
        d2_phi = math.multiply(d2_phi, math.exp(math.multiply(-1, math.pow(math.divide(peakLambda, lambda), 2))));
        var solid_angle = math.multiply(math.divide(math.PI, 4), math.multiply(math.divide(sampleAperture, SDD), math.divide(sampleAperture, SDD)));
        var beamFlux = math.multiply(area, d2_phi, lambdaSpread.toNumeric(), solid_angle, totalTrans);

        this.beamfluxNode.value = beamFlux.toNumeric();
    }
    calculateDistanceFromBeamCenter(nPixels, pixelCenter, pixelSize, coeff) {
        var pixelArray = [...Array(nPixels).keys()].map(i => i + 1);
        var rawValue = math.multiply(math.subtract(pixelArray, pixelCenter), pixelSize, math.unit(1, 'rad'));
        return math.multiply(coeff, math.tan(math.divide(rawValue, coeff)));
    }
    calculateFigureOfMerit() {
        var figureOfMerit = math.multiply(math.pow(this.getWavelength(), 2), this.getBeamFlux())
        this.figureOfMeritNode.value = figureOfMerit.toNumeric();
    }
    calculateMinimumAndMaximumQ(index = 0) {
        var SDD = this.getSampleToDetectorDistance();
        var offset = this.getDetectorOffset();
        var lambda = this.getWavelength();
        var pixelSize = this.detectorOptions[index].pixels.xSize;
        var detWidth = math.multiply(pixelSize, this.detectorOptions[index].pixels.dimensions[0]);
        var bsProjection = this.calculateBeamStopProjection();
        // Calculate Q-maximum and populate the page
        var radial = math.sqrt(math.add(math.pow(math.multiply(0.5, detWidth), 2), math.pow(math.add(math.multiply(0.5, detWidth), offset), 2)));
        var qMaximum = math.multiply(4, math.multiply(math.divide(Math.PI, lambda), math.sin(math.multiply(0.5, math.atan(math.divide(radial, SDD))))));
        this.qMaxNode.value = qMaximum.toNumeric();
        // Calculate Q-minimum and populate the page
        var qMinimum = math.multiply(math.divide(math.PI, lambda), math.divide(math.chain(bsProjection).add(pixelSize).add(pixelSize).done(), SDD));
        this.qMinNode.value = qMinimum.toNumeric();
        // Calculate Q-maximum and populate the page
        var theta = math.atan(math.divide(math.add(math.divide(detWidth, 2.0), offset), SDD));
        var qMaxHorizon = math.chain(4).multiply(math.divide(math.PI, lambda)).multiply(Math.sin(math.multiply(0.5, theta))).done();
        this.qMaxHorizontalNode.value = qMaxHorizon.toNumeric();
        // Calculate Q-maximum and populate the page
        var theta = math.atan(math.divide(math.divide(detWidth, 2.0), SDD));
        var qMaxVert = math.chain(4).multiply(math.divide(math.PI, lambda)).multiply(math.sin(math.multiply(0.5, theta))).done();
        this.qMaxVerticalNode.value = qMaxVert.toNumeric();
    }
    calculateQRangeSlicer(index = 0) {
        var xPixels = this.detectorOptions[index].pixels.dimensions[0];
        var yPixels = this.detectorOptions[index].pixels.dimensions[1];
        var xCenter = this.calculateBeamCenterX(index);
        var yCenter = yPixels / 2 + 0.5;
        var pixelXSize = this.detectorOptions[index].pixels.xSize;
        var pixelYSize = this.detectorOptions[index].pixels.ySize;
        var coeff = this.flux.coeff;
        var lambda = this.getWavelength();
        
        // Detector values pixel size in mm
        var detectorDistance = this.getSampleToDetectorDistance();
        window.intensity2D = generateOnesArray(index);
        window.mask = generateStandardMaskArray(index);

        // Calculate Qx and Qy values
        var xDistance = this.calculateDistanceFromBeamCenter(xPixels, xCenter, pixelXSize, coeff);
        var thetaX = math.divide(math.atan(math.divide(xDistance, detectorDistance)), 2);
        window.qxValues = math.multiply(4, math.divide(Math.PI, lambda), math.sin(thetaX));
        var yDistance = this.calculateDistanceFromBeamCenter(yPixels, yCenter, pixelYSize, coeff);
        var thetaY = math.divide(math.atan(math.divide(yDistance, detectorDistance)), 2);
        window.qyValues = math.multiply(4, math.divide(Math.PI, lambda), math.sin(thetaY));
        window.slicer.calculate();
    }
    calculateSourceToSampleApertureDistance() {
        this.ssdNode.value = math.subtract(this.collimationOptions.lengthMaximum,
            math.subtract(math.subtract(math.multiply(this.collimationOptions.lengthPerUnit, this.getNumberOfGuides()),
            this.sampleTableOptions[this.sampleTableNode.value].offset),
            this.sampleTableOptions[this.sampleTableNode.value].apertureOffset)).toNumeric();
    }
    calculateSampleToDetectorDistance(index = 0) {
        var value = this.getSampleToDetectorDistance(index);
        this.sddNodes[index].value = value.toNumeric();
    }
    calculateWavelengthRange() {
        var currentSpread = this.wavelengthSpreadNode.value;
        var constants = this.wavelengthOptions.spreads[currentSpread].constants;
        var calculatedMinimum = math.add(constants[0], math.divide(constants[1], this.wavelengthOptions.max_rpm));
        var minimum = (calculatedMinimum > this.wavelengthOptions.minimum) ? calculatedMinimum : this.wavelengthOptions.minimum;
        this.wavelengthOptions.spreads[currentSpread].range = [minimum, this.wavelengthOptions.maximum]
        setAttributes(this.wavelengthNode, { 'min': minimum.toNumeric(), 'max': this.wavelengthOptions.maximum.toNumeric() });
        if (this.getWavelength() < minimum) {
            this.wavelengthNode.value = minimum.toNumeric();
        }
    }

    // Various class updaters
    updateWavelength(runSASCALC = true) {
        this.calculateWavelengthRange();
        if (runSASCALC) {
            this.SASCALC();
        }
    }
    updateGuides(runSASCALC = true) {
        // Get guide nodes for the specific instrument
        var allApertureOptions = Object.values(this.sourceApertureNode.options);
        var guideApertureOptions = this.collimationOptions.options[this.guideConfigNode.value].apertureOptions;
        // Show only source apertures allowed for the current guide configuration
        for (var aperture in allApertureOptions) {
            var apertureValue = math.unit(allApertureOptions[aperture].value, 'cm');
            if (math.compare(apertureValue, guideApertureOptions).includes(0)) {
                allApertureOptions[aperture].disabled = false;
                allApertureOptions[aperture].hidden = false;
                allApertureOptions[aperture].selected = true;
            } else {
                allApertureOptions[aperture].disabled = true;
                allApertureOptions[aperture].hidden = true;
            }
        }
        if (runSASCALC) {
            this.SASCALC();
        }
    }

    // Various class getter functions
    // Use these to be sure units are correct
    getAttenuationFactor() {
        return this.attenuationFactorNode.value;
    }
    getAttenuators() {
        return this.attenuatorNode.value;
    }
    getBeamFlux() {
        return math.unit(this.beamfluxNode.value, 'cm^-2s^-1')
    }
    getBeamDiameter(index = 0) {
        return math.unit(this.beamSizeNodes[index].value, 'cm');
    }
    getBeamStopDiameter(index = 0) {
        return math.unit(this.beamStopSizeNodes[index].value, 'inch');
    }
    getNumberOfGuides() {
        var guides = this.guideConfigNode.value;
        if (guides == "LENS") {
            guides = 0;
        } else {
            guides = parseInt(guides);
        }
        return guides;
    }
    getSampleApertureSize() {
        return math.unit(this.sampleApertureNode.value, 'cm');
    }
    getSourceApertureSize() {
        return math.unit(this.sourceApertureNode.value, 'cm');
    }
    getSampleApertureToDetectorDistance(index = 0) {
        var table = this.sampleTableNode.value;
        var offsets = this.sampleTableOptions[table];
        return math.add(math.unit(this.sddInputNodes[index].value, 'cm'), math.add(offsets.offset, offsets.apertureOffset));
    }
    getSampleToDetectorDistance(index = 0) {
        var tableOffset = this.sampleTableOptions[this.sampleTableNode.value].offset;
        var sdd = math.unit(this.sddInputNodes[index].value, 'cm');
        return math.add(sdd, tableOffset);
    }
    getDetectorOffset(index = 0) {
        var detOffset = this.offsetInputNodes[index].value;
        return math.unit(detOffset, 'cm');
    }
    getSourceToSampleDistance() {
        return math.unit(this.ssdNode.value, 'cm');
    }
    getSourceToSampleApertureDistance() {
        var apertureOffset = this.sampleTableOptions[this.sampleTableNode.value].apertureOffset;
        return math.subtract(math.unit(this.ssdNode.value, 'cm'), apertureOffset);
    }
    getWavelength() {
        return math.unit(this.wavelengthNode.value, 'angstrom');
    }
    getWavelengthSpread() {
        return math.unit(this.wavelengthSpreadNode.value, 'percent');
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
            max_rpm: math.unit(5600, 'min^-1'),
            spreads: {
                '10.1': {
                    constants: [math.unit(0.1686, 'angstrom'), math.unit(36510, 'angstrom min^-1')],
                    value: math.unit(10.1, 'pct'),
                    range: [],
                },
                '13.6': {
                    constants: [math.unit(0.0563, 'angstrom'), math.unit(25572, 'angstrom min^-1')],
                    value: math.unit(13.6, 'pct'),
                    range: [],
                    defaultTilt: true,
                },
                '15.0': {
                    constants: [math.unit(0.950, 'angstrom'), math.unit(19000, 'angstrom min^-1')],
                    value: math.unit(15.0, 'pct'),
                    range: [],
                },
                '27.5': {
                    constants: [math.unit(0.0861, 'angstrom'), math.unit(12093, 'angstrom min^-1')],
                    value: math.unit(27.5, 'pct'),
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
                sliderDefaults: [math.unit(100, 'cm'), math.unit(400, 'cm'), math.unit(1300, 'cm'), math.unit(1530, 'cm')],
                offsetRange: [math.unit(0, 'cm'), math.unit(25, 'cm')],
                offsetDefault: math.unit(0, 'cm'),
                offsetSliderDefaults: [math.unit(0, 'cm'), math.unit(25, 'cm')]
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
            b: math.unit(0.0395, 'angstrom^-1'),
            c: math.unit(0.0442, 'angstrom^-1'),
            coeff: math.unit(10000, 'm'),
            peakFlux: math.unit(2.55e13, 'Hz'),
            peakWavelength: math.unit(5.5, 'angstrom'),
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

class NGB10 extends Instrument {
    static instrumentName = "ngb10";
    static hostname = "ngbsans.ncnr.nist.gov";
    static isReal = true;

    constructor() {
        super(NGB10.instrumentName);
    }

    //TODO: Finish populating constants

    calculateSourceToSampleApertureDistance() {
        ssd = math.subtract(this.collimationOptions.lengthMaximum, this.sampleTableOptions[this.sampleTableNode.value].offset);
        if (nGds != 0) {
            ssd = math.subtract(ssd, math.subtract(math.unit(61.9, 'cm'), math.multiply(this.collimationOptions.lengthPerUnit, this.getNumberOfGuides())));
        }
        this.ssdNode.value = math.subtract(ssd, this.sampleTableOptions[this.sampleTableNode.value].apertureOffset);
    }
}