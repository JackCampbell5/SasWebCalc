# FIXME: Convert the instrument class from javascript to python


class Instrument():
    hostname = ''
    isReal = False

    def __init__(name=""):
        self.staticDeviceNodeMap = None
        self.mutableDeviceNodeMap = None
        self.name = name
        self.loadDefaults()
        self.getDeviceNodeMaps()
        self.useRealInstrumentValues()
        self.populatePageDynamically()
        self.setSlicer()
        self.setModel()
        self.setEventHandlers()

    """
        Psuedo-abstract method to initialize constants associated with an instrument
    """
    def loadDefaults():
        raise NotImplementedError('The abstract loadDefaults() method must be implemented by Instrument sub-classes.')
    
    """
        Pseudo-abstract method that populates the information on the page based off of information from the server
    """
    def useRealInstrumentValues():
        raise NotImplementedError('The abstract useRealInstrumentValues() method must be implemented by Instrument sub-classes.')

    """
        Generic method to point to all nodes on the page associated with the instrument
        Standard SANS instruments (both 30m and 10m) should use this method. VSANS Might be able to as well.
    """
    def populatePageDynamically():
        self.instrumentContainer = document.getElementById('instrument')
        if self.instrumentContainer:
            self.instrumentContainer.style.display = "block"
            # Remove all children before populating
            while self.instrumentContainer.firstChild:
                self.instrumentContainer.removeChild(self.instrumentContainer.lastChild)
            # Create a sample table node if sample spaces are an option
            if self.sampleTableOptions:
                self.sampleTableContainer = createChildElement(self.instrumentContainer, 'div', { 'id': 'Sample', 'class': "slidecontainer instrument-section" }, '')
                # createChildElement(self.sampleTableContainer, 'h3', {}, 'Sample Space:')
                self.sampleTableNode = createChildElementWithLabel(self.sampleTableContainer, 'select', { 'id': 'SampleTable' }, '', 'Sample Table: ')
                for sampleTable in self.sampleTableOptions:
                    option = createChildElement(self.sampleTableNode, 'option', { 'value': sampleTable }, sampleTable)
                    if self.sampleTableDefault == sampleTable:
                        option.selected = true
            # Create a wavelength node if wavelength is an option
            if self.wavelengthOptions:
                self.wavelengthContainer = createChildElement(self.instrumentContainer, 'div', { 'id': 'Wavelength', 'class': "slidecontainer instrument-section" }, '')
                # createChildElement(self.wavelengthContainer, 'h3', {}, 'Neutron Wavelength:')
                self.wavelengthNode = createChildElementWithLabel(self.wavelengthContainer, 'input', { 'type': 'number', 'id': 'WavelengthInput', 'value': self.wavelengthOptions.default.toNumeric() }, '', '&lambda (&#8491): ')
                self.wavelengthSpreadNode = createChildElementWithLabel(self.wavelengthContainer, 'select', { 'id': 'WavelengthSpread' }, '', '&Delta&lambda/&lambda (%): ')
                for spreadValue in self.wavelengthOptions.spreads:
                    # createChildElement(self.wavelengthSpreadNode, 'option', { 'value': spreadValue.toString() }, spreadValue)
                    pass

                self.calculateWavelengthRange()

                self.beamfluxNode = createChildElementWithLabel(self.wavelengthContainer, 'input', { 'type': 'number', 'id': 'BeamFlux' }, '', 'Beam Flux (n-cm<sup>-2</sup>-sec<sup>-1</sup>): ')
                self.beamfluxNode.disabled = true
                self.figureOfMeritNode = createChildElementWithLabel(self.wavelengthContainer, 'input', { 'type': 'number', 'id': 'FigureOfMerit' }, '', 'Figure of Merit: ')
                self.figureOfMeritNode.disabled = true
                self.attenuatorNode = createChildElementWithLabel(self.wavelengthContainer, 'input', { 'type': 'number', 'id': 'Attenuators' }, '', 'Attenuators: ')
                self.attenuatorNode.disabled = true
                self.attenuationFactorNode = createChildElementWithLabel(self.wavelengthContainer, 'input', { 'type': 'number', 'id': 'AttenuationFactor' }, '', 'AttenuationFactor: ')
                self.attenuationFactorNode.disabled = true
            # Create a collimationOptions node if collimationOptions is an option
            if self.collimationOptions:
                apertureDict = []
                self.collimationContainer = createChildElement(self.instrumentContainer, 'div', { 'id': 'Collimation', 'class': "slidecontainer instrument-section"}, '')
                createChildElement(self.collimationContainer, 'h3', { 'id': 'Collimation'}, 'Collimation Settings:')
                self.guideConfigNode = createChildElementWithLabel(self.collimationContainer, 'select', { 'id': 'GuideConfig' }, '', 'Guides: ')
                for guideOption in self.collimationOptions.options:
                    optionDict = self.collimationOptions.options[guideOption]
                    for aperture in optionDict.apertureOptions:
                        value = optionDict.apertureOptions[aperture]
                        if not math.compare(value, apertureDict).includes(0):
                            apertureDict.push(value)
                    option = createChildElement(self.guideConfigNode, 'option', { 'value': guideOption }, optionDict.name)
                    if guideOption == self.collimationOptions.guideDefault:
                        option.selected = true
                self.sourceApertureNode = createChildElementWithLabel(self.collimationContainer, 'select', { 'id': 'SourceAperture' }, '', 'Source Aperture: ')
                for key in apertureDict:
                    aperture = apertureDict[key]
                    option = createChildElement(self.sourceApertureNode, 'option', { 'value': aperture.toNumber() }, aperture.toString())
                    if aperture == self.collimationOptions.apertureDefault:
                        option.selected = true
                self.sampleApertureNode = createChildElementWithLabel(self.collimationContainer, 'input', { 'type': 'number', 'value': '1.27', 'id': 'SampleAperture' }, '', 'Sample Aperture (cm): ')
                self.ssdNode = createChildElementWithLabel(self.collimationContainer, 'input', { 'type': 'number', 'id': 'SSD' }, '', 'Source-to-Sample Distance (cm): ')
                self.ssdNode.disabled = true
                self.updateGuides(false)
            if self.detectorOptions:
                self.sddInputNodes = []
                self.sddSliderNodes = []
                self.offsetInputNodes = []
                self.offsetSliderNodes = []
                self.sddNodes = []
                self.beamSizeNodes = []
                self.beamStopSizeNodes = []
                self.detectorContainer = createChildElement(self.instrumentContainer, 'div', { 'id': 'Detector', 'class': "slidecontainer instrument-section" }, '')
                createChildElement(self.detectorContainer, 'h3', {}, 'Detector Settings:')
                for i in self.detectorOptions:
                    # Differentiate multiple detectors, but only if multiple exist
                    if self.detectorOptions.length > 1:
                        # createChildElement(self.detectorContainer, 'h4', {}, 'Detector #' + i)
                        pass
                    index = i if self.detectorOptions.length > 1 else ''
                    detector = self.detectorOptions[i]
                    self.sddInputNodes.push(createChildElementWithLabel(self.detectorContainer, 'input', { 'id': 'SDDInputBox' + index, 'type': 'number', 'min': detector.range[0].toNumeric(), 'max': detector.range[1].toNumeric(), 'value': detector.default.toNumeric() }, '', 'Detector'.concat(index, ' Distance (cm): ')))
                    self.sddSliderNodes.push(createChildElement(self.detectorContainer, 'input', { 'id': 'SDDSliderBar' + index, 'type': 'range', 'class': 'slider', 'list': 'sddDefaults' + index, 'min': detector.range[0].toNumeric(), 'max': detector.range[1].toNumeric(), 'value': detector.default.toNumeric() }, ''))
                    datalist = createChildElement(self.detectorContainer, 'datalist', { 'id': 'sddDefaults' + index }, '')
                    for sliderIndex in detector.sliderDefaults:
                        item = detector.sliderDefaults[sliderIndex]
                        createChildElement(datalist, 'option', { 'value': item.toNumeric(), 'label': item.toNumeric() }, '')
                    self.offsetInputNodes.push(createChildElementWithLabel(self.detectorContainer, 'input', { 'id': 'OffsetInputBox' + index, 'type': 'number', 'min': detector.offsetRange[0].toNumeric(), 'max': detector.offsetRange[1].toNumeric(), 'value': detector.offsetDefault.toNumeric() }, '', 'Detector'.concat(index, ' Offset (cm): ')))
                    self.offsetSliderNodes.push(createChildElement(self.detectorContainer, 'input', { 'id': 'OffsetSliderBar' + index, 'type': 'range', 'class': 'slider', 'list': 'offsetDefaults' + index, 'min': detector.offsetRange[0].toNumeric(), 'max': detector.offsetRange[1].toNumeric(), 'value': detector.offsetDefault.toNumeric() }, ''))
                    datalistOffset = createChildElement(self.detectorContainer, 'datalist', { 'id': 'offsetDefaults' + index }, '')
                    for sliderIndex in detector.offsetSliderDefaults:
                        item = detector.offsetSliderDefaults[sliderIndex]
                        createChildElement(datalistOffset, 'option', { 'value': item.toNumeric(), 'label': item.toNumeric() }, '')
                    self.sddNodes.push(createChildElementWithLabel(self.detectorContainer, 'input', { 'id': 'SDD' + index }, '', 'Sample-To-Detector'.concat(index, ' Distance (cm): ')))
                    self.sddNodes[i].disabled = true
                    self.beamSizeNodes.push(createChildElementWithLabel(self.detectorContainer, 'input', { 'id': 'BeamSize' + index, 'type': 'number' }, '', 'Beam Diameter (cm): '))
                    self.beamSizeNodes[i].disabled = true
                    self.beamStopSizeNodes.push(createChildElementWithLabel(self.detectorContainer, 'input', { 'id': 'BeamStopSize' + index, 'type': 'number' }, '', 'Beam Stop Size (inch): '))
                    self.beamStopSizeNodes[i].disabled = true

            self.qRangeContainer = createChildElement(self.instrumentContainer, 'div', { 'id': 'QRange', 'class': "slidecontainer instrument-section" }, '')
            createChildElement(self.qRangeContainer, 'h3', {}, 'Q Range:')
            self.qMinNode = createChildElementWithLabel(self.qRangeContainer, 'input', { 'id': 'MinimumQ', 'type': 'number' }, '', 'Minimum Q (&#8491<sup>-1</sup>): ')
            self.qMaxNode = createChildElementWithLabel(self.qRangeContainer, 'input', { 'id': 'MaximumQ', 'type': 'number' }, '', 'Maximum Q (&#8491<sup>-1</sup>): ')
            self.qMaxVerticalNode = createChildElementWithLabel(self.qRangeContainer, 'input', { 'id': 'MaximumVerticalQ', 'type': 'number' }, '', 'Maximum Vertical Q (&#8491<sup>-1</sup>): ')
            self.qMaxHorizontalNode = createChildElementWithLabel(self.qRangeContainer, 'input', { 'id': 'MaximumhorizontalQ', 'type': 'number' }, '', 'Maximum Horizontal Q (&#8491<sup>-1</sup>): ')
            if not self.qIsInput:
                self.qMinNode.disabled = true
                self.qMaxNode.disabled = true
                self.qMaxVerticalNode.disabled = true
                self.qMaxHorizontalNode.disabled = true
            else:
                raise TypeError(f'Unknown instrument name: {$self.instrumentName}')

    def setEventHandlers():
        # FIXME: Should this be in js of python?
        # Initialize oninput and onchange events for the given instrument
        def sascalc():
            window.currentInstrument.SASCALC()
        def updateWavelength():
            window.currentInstrument.updateWavelength()
        def updateGuides():
            window.currentInstrument.updateGuides()
        def updateAperture():
            window.currentInstrument.sampleApertureNode.value = self.value
            sascalc()
        def updateDetectorSliderSDD(index=0):
            window.currentInstrument.sddInputNodes[index].value = window.currentInstrument.sddSliderNodes[index].value
            sascalc()
        def updateDetectorInputSDD(index=0):
            window.currentInstrument.sddSliderNodes[index].value = window.currentInstrument.sddInputNodes[index].value
            sascalc()
        def updateDetectorSliderOffset(index=0):
            window.currentInstrument.offsetInputNodes[index].value = window.currentInstrument.offsetSliderNodes[index].value
            sascalc()
        def updateDetectorInputOffset(index=0):
            window.currentInstrument.offsetSliderNodes[index].value = window.currentInstrument.offsetInputNodes[index].value
            sascalc()
        if self.sampleTableNode:
            self.sampleTableNode.onchange = lambda : sascalc() 
        if self.wavelengthContainer:
            self.wavelengthNode.onchange = lambda : updateWavelength()
            self.wavelengthSpreadNode.onchange = lambda : updateWavelength()
        if self.guideConfigNode:
            self.guideConfigNode.onchange = lambda : updateGuides()
        if self.sourceApertureNode:
            self.sourceApertureNode.onchange = lambda : sascalc()
        if self.sampleApertureNode:
            self.sampleApertureNode.onchange = lambda : updateAperture()
        if self.detectorContainer:
            for index in self.detectorOptions.keys():
                self.sddSliderNodes[index].onchange = lambda : updateDetectorSliderSDD(index)
                self.sddInputNodes[index].oninput = lambda : updateDetectorInputSDD(index)
                self.offsetSliderNodes[index].onchange = lambda : updateDetectorSliderOffset(index)
                self.offsetInputNodes[index].oninput = lambda : updateDetectorInputOffset(index)
        if self.qIsInput:
            self.qMinNode.onchange = lambda : sascalc()
            self.qMaxNode.onchange = lambda : sascalc()
            self.qMaxHorizontalNode.onchange = lambda : sascalc()
            self.qMaxVerticalNode.onchange = lambda : sascalc()

    """
        Get the static and active device node maps from the instrument computer
    """
    def getDeviceNodeMaps():
        try:
            if self.isReal and self.hostname != '':
                self.staticDeviceNodeMap = connectToNice(callback = getStaticNodeMap, server = self.hostname)
                self.mutableDeviceNodeMap = connectToNice(callback = getDevicesMap, server = self.hostname)
            # TODO: Remove console output once node names are known and obvious
            for nodeName in self.staticDeviceNodeMap:
                console.log(nodeName + ": " + self.staticDeviceNodeMap[nodeName])
            for nodeName in self.mutableDeviceNodeMap:
                console.log(nodeName + ": " + self.mutableDeviceNodeMap[nodeName])
        except Exception as err:
            logging.warn(f'Unable to connect to remote server: {$self.hostname}')

    def setModelName():
        self.modelNode = document.getElementById('model')
        self.model = self.modelNode.value

    def setModel(runSasCalc = true):
        self.setModelName()
        selectModel(self.model, runSasCalc)

    def setSlicerName():
        self.slicerNode = document.getElementById('averagingType')
        self.slicerName = self.slicerNode.value

    def setSlicer():
        self.setSlicerName()
        slicerSelection(self.slicerName)

    def SASCALC():
        # Calculate any instrument parameters
        # Keep as a separate function so Q-range entries can ignore this
        self.calculateInstrumentParameters()
        # Do average of an array of 1s
        calculateModel()
        # Update the charts
        update1DChart()
        update2DChart()
        # Set current configuration
        setCurrentConfig(self.instrumentName)
        # Store persistant state
        storePersistantState(self.instrumentName)

    def calculateInstrumentParameters():
        # Calculate the beam stop diameter
        self.calculateBeamStopDiameter()
        # Calculate the estimated beam flux
        self.calculateBeamFlux()
        # Calculate the figure of merit
        self.calculateFigureOfMerit()
        # Calculate the number of attenuators
        self.calculateAttenuators()
        # Do Circular Average of an array of 1s
        for index in self.detectorOptions:
            self.calculateMinimumAndMaximumQ(index)
            self.calculateQRangeSlicer(index)

    def calculateAttenuationFactor(index = 0):
        a2 = self.getSampleApertureSize()
        beamDiam = self.getBeamDiameter(index)
        aPixel = self.detectorOptions[index].pixels.xSize
        iPixelMax = self.flux.perPixelMax
        num_pixels = math.multiply(math.divide(math.PI, 4), math.pow(math.divide(math.multiply(0.5, math.add(a2, beamDiam)), aPixel), 2))
        iPixel = math.divide(self.getBeamFlux(), num_pixels)
        atten = 1.0 if iPixel < iPixelMax else math.divide(iPixelMax, iPixel)
        self.attenuationFactorNode.value = atten if atten == 1.0 else atten.toNumeric()

    def calculateAttenuators():
        self.calculateAttenuationFactor()
        atten = self.getAttenuationFactor()
        af = math.add(0.498, math.subtract(math.multiply(math.unit(0.0792, 'angstrom^-1'), self.getWavelength()), math.multiply(math.unit(1.66e-3, 'angstrom^-2'), math.pow(self.getWavelength(), 2))))
        nf = math.multiply(-1, math.divide(math.log(atten), af))
        numAtten = math.ceil(nf)
        if numAtten > 6:
            numAtten = 7 + Math.floor((numAtten - 6) / 2)
        self.attenuatorNode.value = numAtten

    def calculateBeamCenterX(index = 0):
        # Find the number of x pixels in the detector
        xPixels = self.detectorOptions[index].pixels.dimensions[0]
        # Get pixel size in mm and convert to cm
        dr = self.detectorOptions[index].pixels.xSize
        # Get detector offset in cm
        offset = self.getDetectorOffset()
        xCenter = math.add(math.divide(offset, dr), math.add(math.divide(xPixels, 2), 0.5))
        return xCenter

    def calculateBeamDiameter(index = 0, direction = 'maximum'):
        # Update all instrument calculations needed for beam diameter
        self.calculateSourceToSampleApertureDistance()
        self.calculateSampleToDetectorDistance(index)
        # Get instrumental values
        sourceAperture = self.getSourceApertureSize()
        sampleAperture = self.getSampleApertureSize()
        SSD = self.getSourceToSampleApertureDistance()
        SDD = self.getSampleApertureToDetectorDistance(index)
        wavelength = self.getWavelength()
        wavelengthSpread = self.getWavelengthSpread()
        if self.guideConfigNode.value == 'LENS':
            # If LENS configuration, the beam size is the source aperture size
            # FIXME: This is showing -58 cm... Why?!?!
            self.beamSizeNodes[index].value = self.getSourceApertureSize().toNumeric()
        # Calculate beam width on the detector
        beamWidth = math.add(math.multiply(sourceAperture, math.divide(SDD, SSD)),
            math.divide(math.multiply(sampleAperture, math.add(SSD, SDD)), SSD))
        # Beam height due to gravity
        bv3 = math.multiply(math.multiply(math.add(SSD, SDD), SDD), math.pow(wavelength, 2))
        bv4 = math.multiply(bv3, wavelengthSpread)
        bv = math.add(beamWidth, math.multiply(math.unit(0.0000125, 'percent^-1cm^-3'), bv4))
        # Larger of the width*safetyFactor and height
        bm_bs = math.multiply(self.bsFactor, beamWidth)
        bm = bm_bs if bm_bs > bv else bv
        if direction == 'vertical':
            beamDiam = bv
        elif direction == 'horizontal':
            beamDiam = bh
        else:
            beamDiam = bm
        self.beamSizeNodes[index].value = beamDiam.toNumeric()

    def calculateBeamStopDiameter(index = 0):
        self.calculateBeamDiameter(index, 'maximum')
        self.beamStopSizeNodes[index].setAttribute('style', '')
        beamDiam = self.getBeamDiameter(index)
        for i in self.beamstop.keys():
            beamStopIDict = self.beamstop[i]
            if math.compare(beamStopIDict.size, beamDiam) >= 0:
                self.beamStopSizeNodes[index].value = beamStopIDict.size.toNumeric()
                return
        # If this is reached, that means the beam diameter is larger than the largest known beamstop
        self.beamStopSizeNodes[index].value = beamStopIDict.size.toNumeric()
        self.beamStopSizeNodes[index].setAttribute('style', 'color:red')

    def calculateBeamStopProjection(index = 0):
        self.calculateSampleToDetectorDistance(index)
        self.calculateBeamDiameter(index)
        self.calculateBeamStopDiameter(index)
        bsDiam = self.getBeamStopDiameter(index)
        sampleAperture = self.getSampleApertureSize()
        L2 = self.getSampleApertureToDetectorDistance()
        LBeamstop = math.add(math.unit(20.1, 'cm'), math.multiply(1.61, self.getBeamStopDiameter()))  # distance in cm from beamstop to anode plane (empirical)
        return math.add(bsDiam, math.multiply(math.add(bsDiam, sampleAperture), math.divide(LBeamstop, math.subtract(L2, LBeamstop)))) # Return value is in cm

    def calculateBeamFlux():
        # FIXME: Flux calculation is about 7x too high
        # Get constants
        peakLambda = self.flux.peakWavelength
        peakFlux = self.flux.peakFlux
        guideGap = self.collimationOptions.gapAtStart
        guideLoss = self.collimationOptions.transmissionPerUnit
        guideWidth = self.collimationOptions.width
        trans1 = self.flux.trans1
        trans2 = self.flux.trans2
        trans3 = self.flux.trans3
        b = self.flux.b
        c = self.flux.c
        sourceAperture = self.getSourceApertureSize()
        sampleAperture = self.getSampleApertureSize()
        SDD = self.getSampleToDetectorDistance()
        wave = self.getWavelength()
        lambdaSpread = self.getWavelengthSpread()
        guides = self.getNumberOfGuides()

        # Run calculations
        alpha = math.divide(math.add(sourceAperture, sampleAperture), math.multiply(2, SDD))
        f = math.divide(math.multiply(guideGap, alpha), math.multiply(2, guideWidth))
        trans4 = math.multiply(math.subtract(1, f), math.subtract(1, f))
        trans5 = math.exp(math.multiply(guides, Math.log(guideLoss)))
        trans6 = math.subtract(1, math.multiply(wave, math.subtract(b, math.multiply(math.divide(guides, 8), math.subtract(b, c)))))
        totalTrans = math.multiply(trans1, trans2, trans3, trans4, trans5, trans6)

        area = math.chain(math.PI).multiply(sampleAperture.toNumeric()).multiply(sampleAperture.toNumeric()).divide(4).done()
        d2_phi = math.divide(peakFlux, math.multiply(2, math.PI))
        d2_phi = math.multiply(d2_phi, math.exp(math.multiply(4, math.log(math.divide(peakLambda, wave)))))
        d2_phi = math.multiply(d2_phi, math.exp(math.multiply(-1, math.pow(math.divide(peakLambda, wave), 2))))
        solid_angle = math.multiply(math.divide(math.PI, 4), math.multiply(math.divide(sampleAperture, SDD), math.divide(sampleAperture, SDD)))
        beamFlux = math.multiply(area, d2_phi, lambdaSpread.toNumeric(), solid_angle, totalTrans)

        self.beamfluxNode.value = beamFlux.toNumeric()

    def calculateDistanceFromBeamCenter(nPixels, pixelCenter, pixelSize, coeff):
        # FIXME: List comprehension - likely will pass JSON list of lists
        #   -> pass to numpy
        pixelArray = [...Array(nPixels).keys()].map(i => i + 1)
        rawValue = math.multiply(math.subtract(pixelArray, pixelCenter), pixelSize, math.unit(1, 'rad'))
        return math.multiply(coeff, math.tan(math.divide(rawValue, coeff)))

    def calculateFigureOfMerit():
        figureOfMerit = math.multiply(math.pow(self.getWavelength(), 2), self.getBeamFlux())
        self.figureOfMeritNode.value = figureOfMerit.toNumeric()

    def calculateMinimumAndMaximumQ(index = 0):
        SDD = self.getSampleToDetectorDistance()
        offset = self.getDetectorOffset()
        wave = self.getWavelength()
        pixelSize = self.detectorOptions[index].pixels.xSize
        detWidth = math.multiply(pixelSize, self.detectorOptions[index].pixels.dimensions[0])
        bsProjection = self.calculateBeamStopProjection()
        # Calculate Q-maximum and populate the page
        radial = math.sqrt(math.add(math.pow(math.multiply(0.5, detWidth), 2), math.pow(math.add(math.multiply(0.5, detWidth), offset), 2)))
        qMaximum = math.multiply(4, math.multiply(math.divide(Math.PI, wave), math.sin(math.multiply(0.5, math.atan(math.divide(radial, SDD))))))
        self.qMaxNode.value = qMaximum.toNumeric()
        # Calculate Q-minimum and populate the page
        qMinimum = math.multiply(math.divide(math.PI, wave), math.divide(math.chain(bsProjection).add(pixelSize).add(pixelSize).done(), SDD))
        self.qMinNode.value = qMinimum.toNumeric()
        # Calculate Q-maximum and populate the page
        theta = math.atan(math.divide(math.add(math.divide(detWidth, 2.0), offset), SDD))
        qMaxHorizon = math.chain(4).multiply(math.divide(math.PI, wave)).multiply(Math.sin(math.multiply(0.5, theta))).done()
        self.qMaxHorizontalNode.value = qMaxHorizon.toNumeric()
        # Calculate Q-maximum and populate the page
        theta = math.atan(math.divide(math.divide(detWidth, 2.0), SDD))
        qMaxVert = math.chain(4).multiply(math.divide(math.PI, wave)).multiply(math.sin(math.multiply(0.5, theta))).done()
        self.qMaxVerticalNode.value = qMaxVert.toNumeric()

    def calculateQRangeSlicer(index = 0):
        xPixels = self.detectorOptions[index].pixels.dimensions[0]
        yPixels = self.detectorOptions[index].pixels.dimensions[1]
        xCenter = self.calculateBeamCenterX(index)
        yCenter = yPixels / 2 + 0.5
        pixelXSize = self.detectorOptions[index].pixels.xSize
        pixelYSize = self.detectorOptions[index].pixels.ySize
        coeff = self.flux.coeff
        wave = self.getWavelength()
        
        # Detector values pixel size in mm
        detectorDistance = self.getSampleToDetectorDistance()
        window.intensity2D = generateOnesArray(index)
        window.mask = generateStandardMaskArray(index)

        # Calculate Qx and Qy values
        xDistance = self.calculateDistanceFromBeamCenter(xPixels, xCenter, pixelXSize, coeff)
        thetaX = math.divide(math.atan(math.divide(xDistance, detectorDistance)), 2)
        window.qxValues = math.multiply(4, math.divide(Math.PI, wave), math.sin(thetaX))
        yDistance = self.calculateDistanceFromBeamCenter(yPixels, yCenter, pixelYSize, coeff)
        thetaY = math.divide(math.atan(math.divide(yDistance, detectorDistance)), 2)
        window.qyValues = math.multiply(4, math.divide(Math.PI, wave), math.sin(thetaY))
        window.slicer.calculate()

    def calculateSourceToSampleApertureDistance():
        self.ssdNode.value = math.subtract(self.collimationOptions.lengthMaximum,
            math.subtract(math.subtract(math.multiply(self.collimationOptions.lengthPerUnit, self.getNumberOfGuides()),
            self.sampleTableOptions[self.sampleTableNode.value].offset),
            self.sampleTableOptions[self.sampleTableNode.value].apertureOffset)).toNumeric()

    def calculateSampleToDetectorDistance(index = 0):
        value = self.getSampleToDetectorDistance(index)
        self.sddNodes[index].value = value.toNumeric()

    def calculateWavelengthRange():
        currentSpread = self.wavelengthSpreadNode.value
        constants = self.wavelengthOptions.spreads[currentSpread].constants
        calculatedMinimum = math.add(constants[0], math.divide(constants[1], self.wavelengthOptions.max_rpm))
        minimum = calculatedMinimum if calculatedMinimum > self.wavelengthOptions.minimum else self.wavelengthOptions.minimum
        self.wavelengthOptions.spreads[currentSpread].range = [minimum, self.wavelengthOptions.maximum]
        setAttributes(self.wavelengthNode, { 'min': minimum.toNumeric(), 'max': self.wavelengthOptions.maximum.toNumeric() })
        if self.getWavelength() < minimum:
            self.wavelengthNode.value = minimum.toNumeric()

    # Various class updaters
    def updateWavelength(runSASCALC = true):
        self.calculateWavelengthRange()
        if runSASCALC:
            self.SASCALC()

    def updateGuides(runSASCALC = true):
        # Get guide nodes for the specific instrument
        allApertureOptions = Object.values(self.sourceApertureNode.options)
        guideApertureOptions = self.collimationOptions.options[self.guideConfigNode.value].apertureOptions
        # Show only source apertures allowed for the current guide configuration
        for aperture in allApertureOptions:
            apertureValue = math.unit(allApertureOptions[aperture].value, 'cm')
            if math.compare(apertureValue, guideApertureOptions).includes(0):
                allApertureOptions[aperture].disabled = false
                allApertureOptions[aperture].hidden = false
                allApertureOptions[aperture].selected = true
            else:
                allApertureOptions[aperture].disabled = true
                allApertureOptions[aperture].hidden = true
        if runSASCALC:
            self.SASCALC()

    # Various class getter functions
    # Use these to be sure units are correct
    def getAttenuationFactor():
        return self.attenuationFactorNode.value

    def getAttenuators():
        return self.attenuatorNode.value

    def getBeamFlux():
        return math.unit(self.beamfluxNode.value, 'cm^-2s^-1')

    def getBeamDiameter(index = 0):
        return math.unit(self.beamSizeNodes[index].value, 'cm')

    def getBeamStopDiameter(index = 0):
        return math.unit(self.beamStopSizeNodes[index].value, 'inch')

    def getNumberOfGuides():
        guides = self.guideConfigNode.value
        if guides == "LENS":
            guides = 0
        else:
            guides = parseInt(guides)
        return guides

    def getSampleApertureSize():
        return math.unit(self.sampleApertureNode.value, 'cm')

    def getSourceApertureSize():
        return math.unit(self.sourceApertureNode.value, 'cm')

    def getSampleApertureToDetectorDistance(index = 0):
        table = self.sampleTableNode.value
        offsets = self.sampleTableOptions[table]
        return math.add(math.unit(self.sddInputNodes[index].value, 'cm'), math.add(offsets.offset, offsets.apertureOffset))

    def getSampleToDetectorDistance(index = 0):
        tableOffset = self.sampleTableOptions[self.sampleTableNode.value].offset
        sdd = math.unit(self.sddInputNodes[index].value, 'cm')
        return math.add(sdd, tableOffset)

    def getDetectorOffset(index = 0):
        detOffset = self.offsetInputNodes[index].value
        return math.unit(detOffset, 'cm')

    def getSourceToSampleDistance():
        return math.unit(self.ssdNode.value, 'cm')

    def getSourceToSampleApertureDistance():
        apertureOffset = self.sampleTableOptions[self.sampleTableNode.value].apertureOffset
        return math.subtract(math.unit(self.ssdNode.value, 'cm'), apertureOffset)

    def getWavelength():
        return math.unit(self.wavelengthNode.value, 'angstrom')

    def getWavelengthSpread():
        return math.unit(self.wavelengthSpreadNode.value, 'percent')


class NG7SANS(Instrument):
    def __init__():
        super().__init__()