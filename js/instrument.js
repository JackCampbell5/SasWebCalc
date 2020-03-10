/*
 * Base class for all instruments
 */
class Instrument {
    instrumentName = "";
    hostname = "";
    isReal = false;

    constructor() {
        this.loadConstants();
        this.createNodeMap();
        this.populatePageDynamically();
    }

    /*
     * Psuedo-abstract method to create constants associated with the instrument
     */
    loadConstants() {
        throw new TypeError('The abstract loadConstants method must be implemented by Instrument sub-classes.');
    }

    /*
     * Generic method to point to all nodes on the page associated with the instrument
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
                // TODO:
            }
            this.detectorContainer = document.getElementById(this.instrumentName + 'Detector');
            if (this.detectorContainer != null) {
                // TODO: 
            }
            this.qRangeContainer = document.getElementById(this.instrumentName + 'QRange');
            if (this.qRangeContainer != null) {
                // TODO: 
            }
        }
    }

    /*
    * Attempt to populate the page using values taken directly from the instrument
    * Any failed connections will cause the page to use the default values for all inputs
    */
    async populatePageDynamically() {
        return getDeviceNodeMaps();
    }

    /*
     * Get the static and active device node maps from the instrument computer
     */
    getDeviceNodeMaps() {
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
    instrumentName = "ng7";
    hostname = "ng7sans.ncnr.nist.gov";
    isReal = true;
    
    loadConstants() {
        this.sampleTableDefault = "Chamber";
        this.sampleTableOptions = ["Chamber", "Huber"];
        this.sampleToSDDOffsets = [0, 54.8];

        this.wavelengthMin = math.unit(4.0, 'angstrom');
        this.wavelengthMax = math.unit(20.0, 'angstrom');
        this.wavelengthDefault = math.unit(6.0, 'angstrom');
        this.wavelengthSpreadOptions = [9.7, 11.5, 13.9, 22.1];
        this.wavelengthSpreadDefault = 13.9;
        this.guideOptions = { '0': '0 Guides', '1': '1 Guide', '2': '2 Guides', '3': '3 Guides', '4': '4 Guides', '5': '5 Guides', '6': '6 Guides', '7': '7 Guides', '8': '8 Guides', 'LENS': 'LENS'};
        this.guideOptionsDefault = '0';
        this.sourceApertureOptions = { '1.43': '1.43 cm', '2.54': '2.54 cm', '3.81': '3.81 cm', '5.08': '5.08 cm' };
        this.sourceAprtureDefault = '5.08';

        this.sddMin = math.unit(91, 'cm');
        this.sddMax = math.unit(1531, 'cm');
        this.sddDefault = math.unit(100, 'cm');
    }

    populatePageDynamically() {
        var nodeMaps = super.populatePageDynamically();
        var staticNodeMap = nodeMaps[0];
        var deviceMap = NodeMaps[1];
        // Available wavelength spreads
        var wavelengthSpreads = staticNodeMap['wavelengthSpread.wavelengthSpread']['permittedValues'];
        var wavelengthSpreadNode = document.getElementById(this.instrumentName + 'WavelengthSpread');
        if (wavelengthSpreads != null && typeof wavelengthSpreads[Symbol.iterator] === 'function') {
            while (wavelengthSpreadNode.lastChild) {
                wavelengthSpreadNode.removeChild(wavelengthSpreadNode.lastChild);
            }
            for (var wavelengthSpread in wavelengthSpreads) {
                var spread = wavelengthSpreads[wavelengthSpread];
                var option = document.createElement("OPTION");
                var val = Math.round(1000 * parseFloat(spread.val)) / 10;
                option.value = val;
                option.appendChild(document.createTextNode(val));
                wavelengthSpreadNode.appendChild(option);
            }
        }
        // TODO: Populate GUIDES, SOURCE APERTURES, and DETECTOR LIMITS (and wavelength limits?)
        var sourceApertures = staticNodeMap['guide.sourceAperture']['permittedValues'];
        var sourceAperturesGuide1 = staticNodeMap['guide01.key']['permittedValues'];
    }
}