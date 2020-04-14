function slicerSelection(slicer) {
    var averagingParams = getAveragingParams();
    var params = {};
    params['phi'] = math.unit((Math.PI / 180) * averagingParams[0], 'rad');
    params['dPhi'] = math.unit((Math.PI / 180) * averagingParams[1], 'rad');
    params['detectorSections'] = averagingParams[2];
    params['qCenter'] = averagingParams[3];
    params['qWidth'] = averagingParams[4];
    params['aspectRatio'] = averagingParams[5];
    switch (slicer) {
        default:
        case 'circular':
            window.slicer = new Circular(params, window.currentInstrument);
            break;
        case 'sector':
            window.slicer = new Sector(params, window.currentInstrument);
            break;
        case 'rectangular':
            window.slicer = new Rectangular(params, window.currentInstrument);
            break;
        case 'annular':
            window.slicer = new Annular(params, window.currentInstrument);
            break;
        case 'elliptical':
            window.slicer = new Elliptical(params, window.currentInstrument);
            break;
    }
}


/*
 * Base class for all slicers - Uses circular averaging methods
 */
class Slicer {
    constructor(params = {}, instrument = null) {
        // Q and Intensity Values
        this.qxVals = window.qxValues;
        this.qyVals = window.qyValues;
        this.rawIntensity = window.intensity2D;
        // Min/max Q values
        this.maxQx = (Math.max(...this.qxVals) === undefined) ? 0.3 : Math.max(...this.qxVals);
        this.maxQy = (Math.max(...this.qyVals) === undefined) ? 0.3 : Math.max(...this.qyVals);
        this.minQx = (Math.min(...this.qxVals) === undefined) ? 0.0 : Math.min(...this.qxVals);
        this.minQy = (Math.min(...this.qyVals) === undefined) ? 0.0 : Math.min(...this.qyVals);
        // Averaging Parameters
        this.detectorSections = (params['detectorSections'] === undefined) ? 'both' : params['detectorSections'];
        this.phi = math.unit((params['phi'] === undefined) ? 0.0 : parseFloat(params['phi']), 'rad');
        this.dPhi = math.unit((params['dPhi'] === undefined) ? math.divide(math.PI, 2) : parseFloat(params['dPhi']), 'rad');
        this.qCenter = math.unit((params['qCenter'] === undefined) ? 0.0 : parseFloat(params['qCenter']), 'angstrom^-1');
        this.qWidth = math.unit((params['qWidth'] === undefined) ? 0.3 : parseFloat(params['qWidth']), 'angstrom^-1');
        this.aspectRatio = (params['aspectRatio'] === undefined) ? 1.0 : parseFloat(params['aspectRatio']);
        if (instrument) {
            this.instrument = instrument;
            this.lambda = this.instrument.getWavelength();
            this.lambdaWidth = this.instrument.getWavelengthSpread();
            this.guides = this.instrument.guideConfigNode.value;
            this.sourceAperture = this.instrument.getSourceApertureSize();
            this.sampleAperture = this.instrument.getSampleApertureSize();
            this.apertureOffset = this.instrument.sampleTableOptions[this.instrument.sampleTableNode.value]['apertureOffset'];
            this.SSD = this.instrument.getSourceToSampleDistance();
            this.SDD = [];
            this.pixelSize = [];
            this.xBeamCenter = [];
            this.yBeamCenter = [];
            this.beamStopSize = [];
            for (var index in this.instrument.detectorOptions) {
                this.SDD.push(this.instrument.getSampleToDetectorDistance(index));
                this.pixelSize.push(this.instrument.detectorOptions[index]['pixels']['xSize']);
                this.xBeamCenter.push(math.divide(math.add(this.instrument.detectorOptions[index]['pixels']['dimensions'][0], 1), 2));
                this.yBeamCenter.push(math.divide(math.add(this.instrument.detectorOptions[index]['pixels']['dimensions'][1], 1), 2));
                this.beamStopSize.push(this.instrument.getBeamStopDiameter(index));
            }
            this.coeff = this.instrument.flux['coeff'];
        } else {
            // Instrumental Parameters
            this.lambda = math.unit((params['lambda'] === undefined) ? 6.0 : parseFloat(params['lambda']), 'angstrom');
            this.lambdaWidth = math.unit((params['lambdaWidth'] === undefined) ? 0.14 : parseFloat(params['lambdaWidth']), 'angstrom');
            this.guides = (params['guides'] === undefined) ? 0.0 : parseFloat(params['guides']);
            this.sourceAperture = math.unit((params['sourceAperture'] === undefined) ? 25.4 : parseFloat(params['sourceAperture']), 'cm');
            this.sampleAperture = math.unit((params['sampleAperture'] === undefined) ? 6.35 : parseFloat(params['sampleAperture']), 'cm');
            this.apertureOffset = math.unit((params['apertureOffset'] === undefined) ? 5.00 : parseFloat(params['apertureOffset']), 'cm');
            this.beamStopSize = [math.unit((params['beamStopSize'] === undefined) ? 5.08 : parseFloat(params['beamStopSize']), 'inch')];
            this.SSD = [math.unit((params['SSD'] === undefined) ? 1627 : parseFloat(params['SSD']), 'cm')];
            this.SDD = [math.unit((params['SDD'] === undefined) ? 1530 : parseFloat(params['SDD']), 'cm')];
            this.pixelSize = [math.unit((params['pixelSize'] === undefined) ? 5.08 : parseFloat(params['pixelSize']), 'mm')];
            this.coeff = (params['coeff'] === undefined) ? 10000 : parseFloat(params['coeff']);
            this.xBeamCenter = [(params['xBeamCenter'] === undefined) ? 64.5 : parseFloat(params['xBeamCenter'])];
            this.yBeamCenter = [(params['yBeamCenter'] === undefined) ? 64.5 : parseFloat(params['yBeamCenter'])];
        }
        // Calculated parameters
        this.phiUpper = math.add(this.phi, this.dPhi);
        this.phiLower = math.subtract(this.phi, this.dPhi);
        this.phiX = math.cos(this.phi);
        this.phiY = math.sin(this.phi);
        this.phiToURCorner = math.atan(math.divide(this.maxQy, this.maxQx));
        this.phiToULCorner = math.add(math.atan(math.divide(this.maxQy, this.minQx)), math.PI);
        this.phiToLLCorner = math.add(math.atan(math.divide(this.minQy, this.minQx)), math.PI);
        this.phiToLRCorner = math.add(math.atan(math.divide(this.minQy, this.maxQx)), math.multiply(2, math.PI));
    }

    calculate() {
        var largeNumber = 1.0;
        var radiusCenter = 100;
        var data = window.intensity2D;
        var nq = 0
        var numDimensions = 1;
        var center = 1;
        this.qxVals = window.qxValues;
        this.qyVals = window.qyValues;
        for (var detectorIndex in this.SDD) {
            // TODO: Linearize this
            for (var i = 0; i < this.qxVals.length; i++) {
                var qxVal = this.qxVals[i];
                var xDistance = this.calculateDistanceFromBeamCenter(i, "x", detectorIndex);
                var maskI = window.mask[i];
                var dataI = data[i];
                for (var j = 0; j < this.qyVals.length; j++) {
                    var qyVal = this.qyVals[j];
                    if (this.includePixel(qxVal, qyVal, maskI[j])) {
                        var yDistance = this.calculateDistanceFromBeamCenter(j, "y", detectorIndex);
                        var dataPixel = dataI[j];
                        var totalDistance = math.sqrt(math.add(math.multiply(xDistance, xDistance), math.multiply(yDistance, yDistance)));
                        // Break pixels up into a 3x3 grid close to the beam center
                        if (totalDistance.toNumeric() > radiusCenter) {
                            numDimensions = 1;
                            center = 1;
                        } else {
                            numDimensions = 3;
                            center = 2;
                        }
                        var numDSquared = numDimensions * numDimensions;
                        // Loop over sliced pixels
                        for (var k = 1; k <= numDimensions; k++) {
                            var correctedDx = math.add(xDistance, math.divide(math.multiply(math.subtract(k, center), this.pixelSize[detectorIndex]), numDimensions));
                            for (var l = 1; l <= numDimensions; l++) {
                                var correctedDy = math.add(yDistance, math.divide(math.multiply(math.subtract(l, center), this.pixelSize[detectorIndex]), numDimensions));
                                var iRadius = this.getIRadius(correctedDx, correctedDy, detectorIndex);
                                var irMinus1 = math.subtract(iRadius, 1);
                                nq = (iRadius > nq) ? iRadius : nq;
                                let pixI = math.divide(dataPixel, numDSquared);
                                window.aveIntensity[irMinus1] = (window.aveIntensity[irMinus1] === undefined) ? pixI : math.add(window.aveIntensity[irMinus1], pixI);
                                window.dSQ[irMinus1] = (window.dSQ[irMinus1] === undefined) ? math.multiply(dataPixel, pixI) : math.add(window.dSQ[irMinus1], math.multiply(dataPixel, pixI));
                                window.nCells[irMinus1] = (window.nCells[irMinus1] === undefined) ? math.divide(1, numDSquared) : math.add(window.nCells[irMinus1], math.divide(1, numDSquared));
                            }
                        }
                    }
                }
            }
            this.calculateQ(nq, detectorIndex);
            window.aveIntensity = math.dotDivide(window.aveIntensity, window.nCells);
            var aveSQ = math.dotMultiply(window.aveIntensity, window.aveIntensity);
            var aveisq = math.dotDivide(window.dSQ, window.nCells);
            var diff = math.subtract(aveisq, aveSQ);
            window.sigmaAve = math.sqrt(math.dotDivide(diff, math.subtract(window.nCells, 1)));
            this.calculateResolution(detectorIndex);
            for (var i = 0; i < nq; i++) {
                if (window.nCells[i] <= 1 || window.nCells[i] == NaN || window.nCells[i] == null) {
                    window.aveIntensity[i] = (window.nCells[i] == 0 || Number.isNaN(window.nCells[i])) ? 0 : math.divide(window.aveIntensity[i], window.nCells[i]);
                    window.sigmaAve[i] = largeNumber;
                }
            }
        }
    }

    calculateQ(nq, detectorIndex = 0) {
        var q = [...Array(nq).keys()].map(i => i);
        var radius = math.divide(math.multiply(2, q, this.pixelSize[detectorIndex]), 2);
        var theta = math.divide(math.atan(math.divide(radius, this.SDD[detectorIndex])), 2);
        window.qValues = math.multiply(4, math.divide(math.PI, this.lambda), math.sin(theta));
    }

    getIRadius(xVal, yVal, index = 0) {
        return math.ceil(math.divide(math.sqrt(math.add(math.multiply(xVal, xVal), math.multiply(yVal, yVal))), this.pixelSize[index]));
    }

    calculateResolution(detectorIndex = 0) {
        // Define constants
        var velocityNeutron1A = math.unit(3.956e5, 'cm sec^-1');
        var gravityConstant = math.unit(981.0, 'cm sec^-2');
        var smallNumber = 1e-10;
        // Base calculations
        var lp = math.divide(1, math.add(math.divide(1, this.SDD[detectorIndex]), math.divide(1, this.SSD)));
        // Calculate variances
        var varLambda = math.divide(math.multiply(this.lambdaWidth, this.lambdaWidth), this.lambda);
        if (Boolean(this.guides === "LENS")) {
            var varBeam = math.multiply(0.25, math.add(math.pow(math.divide(math.multiply(this.sourceAperture, this.SDD[detectorIndex]), this.SSD), 2), math.pow(math.divide(math.multiply(this.sampleAperture, this.SDD[detectorIndex], this.lambdaWidth, 2), math.multiply(3, this.lambda, lp)), 2)));
        } else {
            var varBeam = math.multiply(0.25, math.add(math.pow(math.divide(math.multiply(this.sourceAperture, this.SDD[detectorIndex]), this.SSD), 2), math.pow(math.divide(math.multiply(this.sampleAperture, this.SDD[detectorIndex]), lp), 2)));
        }
        var varDetector = math.add(math.dotMultiply(math.divide(this.pixelSize[detectorIndex], 2.3548), math.divide(this.pixelSize[detectorIndex], 2.3548)), math.divide(math.multiply(this.pixelSize[detectorIndex], this.pixelSize[detectorIndex]), 12));
        var velocityNeutron = math.divide(velocityNeutron1A, this.lambda);
        var varGravity = math.divide(math.multiply(0.5, gravityConstant, this.SDD[detectorIndex], math.add(this.SSD, this.SDD[detectorIndex])), math.pow(velocityNeutron, 2));
        var rZero = math.dotMultiply(this.SDD[detectorIndex], math.tan(math.dotMultiply(2.0, math.asin(math.divide(math.dotMultiply(this.lambda, window.qValues), math.multiply(4.0, Math.PI))))));
        var negRZero = math.dotMultiply(rZero, -1);
        var delta = math.dotDivide(math.dotMultiply(0.5, math.dotMultiply(math.add(negRZero, this.beamStopSize[detectorIndex]), math.add(negRZero, this.beamStopSize[detectorIndex]))), varDetector);

        // FIXME: Find usable incomplete gamma function in javascript (or php)
        var incGamma = smallNumber;
        //if (rZero < beamStopSize) {
        //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 - gammainc(1.5, delta) / math.gamma(1.5));
        //} else {
        //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 + window.gammainc(1.5, delta) / math.gamma(1.5));
        //}

        var fSubS = math.dotMultiply(0.5, (math.add(1.0, math.erf(math.dotDivide(math.subtract(rZero, this.beamStopSize[detectorIndex]), math.sqrt(math.multiply(2.0, varDetector)))))));
        for (var i in fSubS) {
            if (fSubS[i] < smallNumber) {
                fSubS[i] = smallNumber;
            }
        }
        var fr = math.add(1.0, math.dotDivide(math.dotMultiply(math.sqrt(varDetector), math.exp(math.multiply(- 1.0, delta))), math.dotMultiply(math.dotMultiply(rZero, fSubS), math.sqrt(math.multiply(2.0, Math.PI)))));
        var fv = math.subtract(math.dotDivide(incGamma, math.dotMultiply(fSubS, math.sqrt(Math.PI))), math.dotDivide(math.dotMultiply(math.dotMultiply(math.dotMultiply(rZero, rZero), math.subtract(fr, 1.0)), math.subtract(fr, 1.0)), varDetector));
        // FIXME: Units of fr and rZero should both be in length - fr unitless
        var rmd = math.add(fr, rZero);
        var varR1 = math.add(varBeam, math.dotMultiply(varDetector, fv), varGravity);
        var rm = math.add(rmd, math.dotDivide(math.dotMultiply(0.5, varR1), rmd));
        var varR = math.subtract(varR1, math.multiply(0.5, math.pow(math.divide(varR1, rmd), 2)));
        for (var i in varR) {
            if (varR[i] < 0.0) {
                varR[i] = 0.0;
            }
        }
        window.qAverage = math.dotMultiply(math.dotDivide(math.dotMultiply(4.0, Math.Pi), this.lambda), math.sin(math.dotMultiply(0.5, math.atan(math.dotDivide(rm, this.SDD[detectorIndex])))));
        window.sigmaQ = math.dotMultiply(window.qAverage, math.sqrt(math.add(math.pow(math.dotDivide(varR, rmd), 2), varLambda)));
        window.fSubs = fSubS;
    }

    includePixel(xVal, yVal, mask) {
        return (mask === 0);
    }

    createPlot() {
        return [];
    }

    calculateDistanceFromBeamCenter(i, xOrY, index = 0) {
        if (xOrY.toLowerCase() === "x")
            var pixelCenter = this.xBeamCenter[index];
        else {
            var pixelCenter = this.yBeamCenter[index];
        }
        return math.multiply(this.coeff, math.tan(math.divide(math.multiply(math.subtract(i, pixelCenter), this.pixelSize[index]), this.coeff)));
    }
}

/*
 * Circular averaging class
 */
class Circular extends Slicer{
}

/*
 * Sector averaging class
 */
class Sector extends Slicer {

    includePixel(xVal, yVal, mask) {
        var pixelAngle = Math.atan(yVal / xVal);
        var isCorrectAngle = (pixelAngle > this.phiLower) && (pixelAngle < this.phiUpper);
        var forward = (isCorrectAngle && xVal > 0);
        var mirror = (isCorrectAngle && xVal < 0);
        var both = (this.detectorSections == "both" && (mirror || forward));
        var left = (this.detectorSections == "left" && mirror);
        var right = (this.detectorSections == "right" && forward);
        return ((both || right || left) && (mask === 0));
    }

    createPlot() {
        var shapes = super.createPlot();
        var detector = this.detectorSections;
        var phi = this.phi;
        var phiUp = this.phiUpper;
        var phiDown = this.phiLower;
        var phiPi = this.phi + math.PI;
        var phiUpPi = this.phiUpper + Math.PI;
        var phiDownPi = this.phiLower + Math.PI;
        if (detector == "both" || detector == "right") {
            // Center of sector
            shapes.push(makeShape('line', 0, 0, (phi > this.phiToURCorner && phi < this.phiToULCorner) ? this.maxQy / Math.tan(phi) : this.maxQx,
                (phi > this.phiToURCorner && phi < this.phiToULCorner) ? this.maxQy : this.maxQx * Math.tan(phi)));
            // Top of sector
            shapes.push(makeShape('line', 0, 0, (phiUp > this.phiToURCorner && phiUp < this.phiToULCorner) ? this.maxQy / Math.tan(phiUp) : this.maxQx,
                (phiUp > this.phiToURCorner && phiUp < this.phiToULCorner) ? this.maxQy : this.maxQx * Math.tan(phiUp), "orange"));
            // Bottom of sector
            shapes.push(makeShape('line', 0, 0, (phiDown > this.phiToURCorner && phiDown < this.phiToULCorner) ? this.maxQy / Math.tan(phiDown) : this.maxQx,
                (phiDown > this.phiToURCorner && phiDown < this.phiToULCorner) ? this.maxQy : this.maxQx * Math.tan(phiDown), "orange"));
        }
        if (detector == "both" || detector == "left") {
            // Center of sector
            shapes.push(makeShape('line', 0, 0, (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner) ? this.minQy / Math.tan(phiPi) : this.minQx,
                (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner) ? this.minQy : this.minQx * Math.tan(phiPi)));
            // Bottom of sector
            shapes.push(makeShape('line', 0, 0, (phiUpPi > this.phiToLLCorner && phiUpPi < this.phiToLRCorner) ? this.minQy / Math.tan(phiUpPi) : this.minQx,
                (phiUpPi > this.phiToLLCorner && phiUpPi < this.phiToLRCorner) ? this.minQy : this.minQx * Math.tan(phiUpPi), "orange"));
            // Top of sector
            shapes.push(makeShape('line', 0, 0, (phiDownPi > this.phiToLLCorner && phiDownPi < this.phiToLRCorner) ? this.minQy / Math.tan(phiDownPi) : this.minQx,
                (phiDownPi > this.phiToLLCorner && phiDownPi < this.phiToLRCorner) ? this.minQy : this.minQx * Math.tan(phiDownPi), "orange"));
        }
        return shapes;
    }

    calculateResolution(i) {
        super.calculateResolution(i);
    }
}

/*
 * Rectangular
 * averaging class
 */
class Rectangular extends Slicer {

    calculateQ(theta) {
        return super.calculateQ(theta);
    }

    includePixel(xVal, yVal, mask) {
        var correctedRadius = Math.sqrt(xVal * xVal + yVal * yVal);
        var dotProduct = (xVal * this.phiX + yVal * this.phiY) / correctedRadius;
        var dPhiPixel = Math.acos(dotProduct);
        var dPerpendicular = correctedRadius * Math.sin(dPhiPixel);
        var a = (dPerpendicular <= 0.5 * this.qWidth * this.pixelSize);
        var b = (this.detectorSections == "both");
        var c = (this.detectorSections == "left" && dotProduct >= 0);
        var d = (this.detectorSections == "right" && dotProduct < 0);
        return  a && (b || c || d) && (mask === 0);
    }

    createPlot() {
        var shapes = super.createPlot();
        var phiPi = math.add(this.phi, math.PI);
        var deltax = isFinite(this.qWidth / (2 * Math.sin(this.phi))) ? this.qWidth / (2 * Math.sin(this.phi)) : 0;
        var deltay = isFinite(this.qWidth / (2 * Math.cos(this.phi))) ? this.qWidth / (2 * Math.cos(this.phi)) : 0;
        var mainInUpper = (this.phi > this.phiToURCorner && this.phi < this.phiToULCorner);
        var mainInLower = (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner);
        var mainQxRight = mainInUpper ? this.maxQy / Math.tan(this.phi) : this.maxQx;
        var mainQxLeft = mainInLower ? this.minQy / Math.tan(this.phi) : this.minQx;
        var mainQyRight = mainInUpper ? this.maxQy : math.multiply(this.maxQx, math.tan(this.phi));
        var mainQyLeft = mainInLower ? this.minQy : math.multiply(this.minQx, math.tan(this.phi));
        if (this.detectorSections == "both" || this.detectorSections == "right") {
            // Center of rectangle
            shapes.push(makeShape('line', 0, 0, mainQxRight, mainQyRight));
            // Top of rectangle
            shapes.push(makeShape('line', 0, deltay, (math.add(mainQyRight, deltay) > this.maxQy) ? this.maxQx : math.add(mainQxRight, deltax),
                (math.add(mainQxRight, deltax) > this.maxQx) ? math.add(mainQyRight, deltay) : this.maxQy, "orange"));
            // Bottom of rectangle
            shapes.push(makeShape('line', 0, -1 * deltay, (math.add(mainQxRight, deltax) > this.maxQx) ? this.maxQx : math.subtract(mainQxRight, deltax),
                (math.subtract(mainQyRight, deltay) > this.maxQy) ? this.maxQy : math.subtract(mainQyRight, deltay), "orange"));
        }
        if (this.detectorSections == "both" || this.detectorSections == "left") {
            // Center of rectangle
            shapes.push(makeShape('line', 0, 0, mainQxLeft, mainQyLeft));
        }
        return shapes;
    }
}

/*
 * Circular averaging class
 */
class Elliptical extends Circular {

    calculateQ(theta) {
        // FIXME: This needs to know the pixel position
        return super.calculateQ(theta);
    }

    calculateRadius(xVal, yVal) {
        var iCircular = super.calculateRadius(xVal, yVal);
        var rho = math.subtract(math.atan(math.divide(xVal, yVal)), this.phi);
        return math.ceil(math.add(math.multiply(iCircular, math.sqrt(math.multiply(math.cos(rho), math.cos(rho)))), math.multiply(this.aspectRatio, this.aspectRatio, math.sin(rho), math.sin(rho))));
    }
}
