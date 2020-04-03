/*
 * Base class for all slicers - Uses circular averaging methods
 */
class Slicer {
    constructor(params = {}, instrument = null) {
        // Q and Intensity Values
        this.qxVals = window.qxValues;
        this.qyVals = window.qyValues;
        this.rawIntensity = window.intensity2D;
        if (instrument) {
            this.instrument = instrument;
            this.lambda = this.instrument.wavelengthNode.value;
            this.lambdaWidth = this.instrument.wavelengthSpreadNode.value;
            this.guides = this.instrument.guideConfigNode.value;
            this.sourceAperture = this.instrument.sourceApertureNode.value;
            this.sampleAperture = this.instrument.sampleApertureNode.value;
            this.apertureOffset = this.instrument.sampleTableOptions[this.instrument.sampleTableNode.value]['apertureOffset'];
            this.SSD = this.instrument.ssdNode.value;
            this.SDD = [];
            this.pixelSize = [];
            this.xBeamCenter = [];
            this.yBeamCenter = [];
            this.beamStopSize = [];
            for (var index in this.instrument.detectorOptions) {
                this.SDD.push(this.instrument.sddInputNodes[index].value);
                this.pixelSize.push(this.instrument.detectorOptions[index]['pixels']['xSize']);
                this.xBeamCenter.push((this.instrument.detectorOptions[index]['pixels']['dimensions'][0] + 1) / 2);
                this.yBeamCenter.push((this.instrument.detectorOptions[index]['pixels']['dimensions'][1] + 1) / 2);
                this.beamStopSize.push(this.instrument.beamStopSizeNodes[index].value);
            }
            this.coeff = this.instrument.flux['coeff'];
        } else {
            // Min/max Q values
            this.maxQx = (Math.max(...this.qxVals) === undefined) ? 0.3 : Math.max(...this.qxVals);
            this.maxQy = (Math.max(...this.qyVals) === undefined) ? 0.3 : Math.max(...this.qyVals);
            this.minQx = (Math.min(...this.qxVals) === undefined) ? 0.0 : Math.min(...this.qxVals);
            this.minQy = (Math.min(...this.qyVals) === undefined) ? 0.0 : Math.min(...this.qyVals);
            // Averaging Parameters
            this.detectorSections = (params['detectorSections'] === undefined) ? 'both' : params['detectorSections'];
            this.phi = (params['phi'] === undefined) ? 0.0 : parseFloat(params['phi']);
            this.dPhi = (params['dPhi'] === undefined) ? Math.PI / 2 : parseFloat(params['dPhi']);
            this.qCenter = (params['qCenter'] === undefined) ? 0.0 : parseFloat(params['qCenter']);
            this.qWidth = (params['qWidth'] === undefined) ? 0.3 : parseFloat(params['qWidth']);
            this.aspectRatio = (params['aspectRatio'] === undefined) ? 1.0 : parseFloat(params['aspectRatio']);
            // Instrumental Parameters
            this.lambda = (params['lambda'] === undefined) ? 6.0 : parseFloat(params['lambda']);
            this.lambdaWidth = (params['lambdaWidth'] === undefined) ? 0.14 : parseFloat(params['lambdaWidth']);
            this.guides = (params['guides'] === undefined) ? 0.0 : parseFloat(params['guides']);
            this.sourceAperture = (params['sourceAperture'] === undefined) ? 25.4 : parseFloat(params['sourceAperture']);
            this.sampleAperture = (params['sampleAperture'] === undefined) ? 6.35 : parseFloat(params['sampleAperture']);
            this.apertureOffset = (params['apertureOffset'] === undefined) ? 5.00 : parseFloat(params['apertureOffset']);
            this.beamStopSize = (params['beamStopSize'] === undefined) ? 5.08 : parseFloat(params['beamStopSize']);
            this.SSD = (params['SSD'] === undefined) ? 1627 : parseFloat(params['SSD']);
            this.SDD = (params['SDD'] === undefined) ? 1530 : parseFloat(params['SDD']);
            this.pixelSize = (params['pixelSize'] === undefined) ? 5.08 : parseFloat(params['pixelSize']);
            this.coeff = (params['coeff'] === undefined) ? 10000 : parseFloat(params['coeff']);
            this.xBeamCenter = (params['xBeamCenter'] === undefined) ? 64.5 : parseFloat(params['xBeamCenter']);
            this.yBeamCenter = (params['yBeamCenter'] === undefined) ? 64.5 : parseFloat(params['yBeamCenter']);
        }
        // Calculated parameters
        this.phiUpper = this.phi + this.dPhi;
        this.phiLower = this.phi - this.dPhi;
        this.phiX = Math.cos(this.phi);
        this.phiY = Math.sin(this.phi);
        this.phiToURCorner = Math.atan(this.maxQy / this.maxQx);
        this.phiToULCorner = Math.atan(this.maxQy / this.minQx) + Math.PI;
        this.phiToLLCorner = Math.atan(this.minQy / this.minQx) + Math.PI;
        this.phiToLRCorner = Math.atan(this.minQy / this.maxQx) + 2 * Math.PI;
    }

    calculate() {
        var nq = 0;
        var largeNumber = 1.0;
        var radiusCenter = 100;
        var data = window.intensity2D;
        var dataI = new Array();
        var maskI = new Array();
        var numDimensions = 1;
        var center = 1;

        for (var i = 0; i < this.qxVals.length; i++) {
            var qxVal = this.qxVals[i];
            var xDistance = this.calculateDistanceFromBeamCenter(i, "x");
            maskI = window.mask[i];
            dataI = data[i];
            for (var j = 0; j < this.qyVals.length; j++) {
                var qyVal = this.qyVals[j];
                if (this.includePixel(qxVal, qyVal, maskI[j])) {
                    var yDistance = this.calculateDistanceFromBeamCenter(j, "y");
                    var dataPixel = dataI[j];
                    var totalDistance = Math.sqrt(xDistance * xDistance + yDistance * yDistance);
                    // Break pixels up into a 3x3 grid close to the beam center
                    if (totalDistance > radiusCenter) {
                        numDimensions = 1;
                        center = 1;
                    } else {
                        numDimensions = 3;
                        center = 2;
                    }
                   var numDSquared = numDimensions * numDimensions;
                    // Loop over sliced pixels
                    for (var k = 1; k <= numDimensions; k++) {
                        var correctedDx = xDistance + (k - center) * this.pixelSize / numDimensions;
                        for (var l = 1; l <= numDimensions; l++) {
                            var correctedDy = yDistance + (l - center) * this.pixelSize / numDimensions;
                            var iRadius = this.getIRadius(correctedDx, correctedDy);
                            var irMinus1 = iRadius - 1;
                            nq = (iRadius > nq) ? iRadius : nq;
                            window.aveIntensity[irMinus1] = (window.aveIntensity[irMinus1] === undefined) ? dataPixel / numDSquared : window.aveIntensity[irMinus1] + dataPixel / numDSquared;
                            window.dSQ[irMinus1] = (window.dSQ[irMinus1] === undefined) ? dataPixel * dataPixel / numDSquared : window.dSQ[irMinus1] + dataPixel * dataPixel / numDSquared;
                            window.nCells[irMinus1] = (window.nCells[irMinus1] === undefined) ? 1 / numDSquared : window.nCells[irMinus1] + 1 / numDSquared;
                        }
                    }
                }
            }
        }
        for (var i = 0; i < nq; i++) {
            this.calculateQ(i);
            if (window.nCells[i] <= 1) {
                window.aveIntensity[i] = (window.nCells[i] == 0 || Number.isNaN(window.nCells[i])) ? 0 : window.aveIntensity[i] / window.nCells[i];
                window.sigmaAve[i] = largeNumber;
            } else {
                window.aveIntensity[i] = isNaN(window.nCells[i]) ? window.aveIntensity[i] : window.aveIntensity[i] / window.nCells[i];
                var aveSQ = window.aveIntensity[i] * window.aveIntensity[i];
                var aveisq = isNaN(window.nCells[i]) ? window.dSQ[i] : window.dSQ[i] / window.nCells[i];
                var diff = aveisq - aveSQ;
                window.sigmaAve[i] = (diff < 0) ? largeNumber : Math.sqrt(diff / (window.nCells[i] - 1));
            }
            if (window.qValues[i] > 0.0) {
                this.calculateResolution(i);
            }
        }
    }

    calculateQ(i) {
        var radius = (2 * i) * this.pixelSize / 2;
        var theta = Math.atan(radius / this.SDD) / 2;
        window.qValues[i] = (4 * Math.PI / this.lambda) * Math.sin(theta);
    }

    getIRadius(xVal, yVal) {
        return Math.floor(Math.sqrt(xVal * xVal + yVal * yVal) / this.pixelSize) + 1;
    }

    calculateResolution(i) {
        // Define constants
        var velocityNeutron1A = 3.956e5;
        var gravityConstant = 981.0;
        var smallNumber = 1e-10;
        var isLenses = Boolean(this.guides === "LENS");
        var qValue = window.qValues[i];
        var pixelSize = this.pixelSize * 0.1
        // Base calculations
        var lp = 1 / (1 / this.SDD + 1 / this.SSD);
        // Calculate variances
        var varLambda = this.lambdaWidth * this.lambdaWidth / 6.0;
        if (isLenses) {
            var varBeam = 0.25 * Math.pow(this.sourceAperture * this.SDD / this.SSD, 2) + 0.25 * (2 / 3) * Math.pow(this.lambdaWidth / this.lambda, 2) * Math.pow(this.sampleAperture * this.SDD / lp, 2);
        } else {
            var varBeam = 0.25 * Math.pow(this.sourceAperture * this.SDD / this.SSD, 2)  + 0.25 * Math.pow(this.sampleAperture * this.SDD / lp, 2);
        }
        var varDetector = Math.pow(pixelSize / 2.3548, 2) + (pixelSize * pixelSize) / 12;
        var velocityNeutron = velocityNeutron1A / this.lambda;
        var varGravity = 0.5 * gravityConstant * this.SDD * (this.SSD + this.SDD) / Math.pow(velocityNeutron, 2);
        var rZero = this.SDD * Math.tan(2.0 * Math.asin(this.lambda * qValue / (4.0 * Math.PI)));
        var delta = 0.5 * Math.pow(this.beamStopSize - rZero, 2) / varDetector;

        // FIXME: Find usable incomplete gamma function in javascript (or php)
        var incGamma = smallNumber;
        //if (rZero < beamStopSize) {
        //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 - gammainc(1.5, delta) / math.gamma(1.5));
        //} else {
        //    var incGamma = Math.exp(Math.log(math.gamma(1.5))) * (1 + window.gammainc(1.5, delta) / math.gamma(1.5));
        //}
        var fSubS = 0.5 * (1.0 + math.erf((rZero - this.beamStopSize) / Math.sqrt(2.0 * varDetector)));
        if (fSubS < smallNumber) {
            fSubS = smallNumber;
        }
        var fr = 1.0 + Math.sqrt(varDetector) * Math.exp(-1.0 * delta) / (rZero * fSubS * math.sqrt(2.0 * Math.PI));
        var fv = incGamma / (fSubS * Math.sqrt(Math.PI)) - rZero * rZero * Math.pow(fr - 1.0, 2) / varDetector;
        var rmd = fr + rZero;
        var varR1 = varBeam + varDetector * fv + varGravity;
        var rm = rmd + 0.5 * varR1 / rmd;
        var varR = varR1 - 0.5 * (varR1 / rmd) * (varR1 / rmd);
        if (varR < 0) {
            varR = 0.0;
        }
        window.qAverage[i] = (4.0 * Math.Pi / this.lambda) * Math.sin(0.5 * Math.atan(rm / this.SDD));
        window.sigmaQ[i] = window.qAverage[i] * Math.sqrt((varR / rmd) * (varR / rmd) + varLambda);
        window.fSubs[i] = fSubS;
    }

    includePixel(xVal, yVal, mask) {
        return (mask === 0);
    }

    createPlot() {
        return [];
    }

    calculateDistanceFromBeamCenter(pixelValue, xOrY) {
        if (xOrY.toLowerCase() === "x")
            var pixelCenter = this.xBeamCenter;
        else {
            var pixelCenter = this.yBeamCenter;
        }
        return this.coeff * Math.tan((pixelValue - pixelCenter) * this.pixelSize / this.coeff);
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
        var phiPi = this.phi + math.PI;
        var deltax = isFinite(this.qWidth / (2 * Math.sin(this.phi))) ? this.qWidth / (2 * Math.sin(this.phi)) : 0;
        var deltay = isFinite(this.qWidth / (2 * Math.cos(this.phi))) ? this.qWidth / (2 * Math.cos(this.phi)) : 0;
        var mainInUpper = (this.phi > this.phiToURCorner && this.phi < this.phiToULCorner);
        var mainInLower = (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner);
        var mainQxRight = mainInUpper ? this.maxQy / Math.tan(this.phi) : this.maxQx;
        var mainQxLeft = mainInLower ? this.minQy / Math.tan(this.phi) : this.minQx;
        var mainQyRight = mainInUpper ? this.maxQy : this.maxQx * Math.tan(this.phi);
        var mainQyLeft = mainInLower ? this.minQy : this.minQx * Math.tan(this.phi);
        if (this.detectorSections == "both" || this.detectorSections == "right") {
            // Center of rectangle
            shapes.push(makeShape('line', 0, 0, mainQxRight, mainQyRight));
            // Top of rectangle
            shapes.push(makeShape('line', 0, deltay, (mainQyRight + deltay > this.maxQy) ? this.maxQx : mainQxRight + deltax,
                (mainQxRight + deltax > this.maxQx) ? mainQyRight + deltay : this.maxQy, "orange"));
            // Bottom of rectangle
            shapes.push(makeShape('line', 0, -1 * deltay, (mainQxRight + deltax > this.maxQx) ? this.maxQx : mainQxRight - deltax,
                (mainQyRight - deltay > this.maxQy) ? this.maxQy : mainQyRight - deltay, "orange"));
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
        var rho = Math.atan(xVal / yVal) - this.phi;
        return Math.floor(iCircular * Math.sqrt(Math.cos(rho) * Math.cos(rho) + this.aspectRatio * this.aspectRatio * Math.sin(rho) * Math.sin(rho))) + 1;
    }
}
