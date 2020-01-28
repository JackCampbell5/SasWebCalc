/*
 * Base class for all slicers - Uses circular averaging methods
 */
class Slicer {
    constructor(params = {}) {
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
        this.phi = (params['phi'] === undefined) ? 0.0 : parseFloat(params['phi']) * Math.PI / 180;
        this.dPhi = (params['dPhi'] === undefined) ? Math.PI / 2 : parseFloat(params['dPhi']) * Math.PI / 180;
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
        // Calculated parameters
        this.phiUpper = phi - dPhi;
        this.phiLower = phi + dPhi;
        this.phiX = Math.cos(phi);
        this.phiY = Math.sin(phi);
        this.phiToURCorner = Math.atan(this.maxQy / this.maxQx);
        this.phiToULCorner = Math.atan(this.maxQy / this.minQx);
        this.phiToLLCorner = Math.atan(this.minQy / this.minQx);
        this.phiToLRCorner = Math.atan(this.minQy / this.maxQx);
    }

    calculate() {
        var tempQArray = [];
        var tempIMap = {};
        var tempDSQMap = {};
        var tempNCellsMap = {};
        var largeNumber = 1.0;
        var data = window.intensity2D;
        var dataI = new Array();

        for (var i = 0; i < this.qxVals.length; i++) {
            var qxVal = this.qxVals[i];
            dataI = data[i];
            for (var j = 0; j < this.qyVals.length; j++) {
                var qyVal = this.qyVals[j];
                var dataPixel = dataI[j];
                if (this.includePixel(qxVal, qyVal)) {
                    var qCurrent = Math.round(this.calculateQ(qxVal, qyVal) * 10000) / 10000;
                    tempQArray.push(qCurrent);
                    tempIMap[qCurrent] = (qCurrent in tempIMap) ? tempIMap[qCurrent] + dataPixel : dataPixel;
                    tempDSQMap[qCurrent] = (qCurrent in tempDSQMap) ? tempDSQMap[qCurrent] + dataPixel * dataPixel : dataPixel * dataPixel;
                    tempNCellsMap[qCurrent] = (qCurrent in tempNCellsMap) ? tempNCellsMap[qCurrent] + 1 : 1;
                }
            }
        }
        var sortedQValues = [...new Set(tempQArray)];
        sortedQValues.sort(function (a, b) { return a - b });
        var k = 0;
        for (var i = 0; i < sortedQValues.length; i += 30) {
            var qValue = sortedQValues[i];
            window.qValues[k] = qValue;
            window.aveIntensity[k] = tempIMap[qValue];
            window.dSQ[k] = tempDSQMap[qValue];
            window.nCells[k] = tempNCellsMap[qValue];
            if (window.nCells[k] <= 1) {
                window.aveIntensity[k] = (window.nCells[k] == 0 || Number.isNaN(window.nCells[k])) ? 0 : window.aveIntensity[k] / window.nCells[k];
                window.sigmaAve[k] = largeNumber;
            } else {
                window.aveIntensity[k] = window.aveIntensity[k] / window.nCells[k];
                var aveSQ = window.aveIntensity[k] * window.aveIntensity[k];
                var aveisq = window.dSQ[k] / window.nCells[k];
                var diff = aveisq - aveSQ;
                window.sigmaAve[k] = (diff < 0) ? largeNumber : Math.sqrt(diff / (window.nCells[k] - 1));
            }
            this.calculateResolution(k);
            k++;
        }
    }

    calculateQ(qxVal, qyVal) {
        return Math.sqrt(qxVal * qxVal + qyVal * qyVal);
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

    includePixel(xVal, yVal) {
        return true;
    }

    createPlot() {
        return [];
    }
}

/*
 * Circular averaging class
 */
class Circular extends Slicer{
    constructor(params) {
        super(params);
    }
}

/*
 * Sector averaging class
 */
class Sector extends Slicer {
    constructor(params) {
        super(params);
    }

    includePixel(xVal, yVal) {
        var pixelAngle = Math.atan(Math.abs(yVal) / Math.abs(xVal));
        var isCorrectAngle = (pixelAngle > this.phiLower) && (pixelAngle < this.phiUpper);
        var isCorrectAngleMirror = (pixelAngle > this.phiLower) && (pixelAngle < this.phiUpper);
        var forward = (isCorrectAngle && xVal > 0);
        var mirror = (isCorrectAngleMirror && xVal < 0);
        var both = (this.detectorSections == "both" && (mirror || forward));
        var left = (this.detectorSections == "left" && mirror);
        var right = (this.detectorSections = "right" && forward);
        return (both || right || left);
    }

    createPlot() {
        var shapes = super.createPlot();
        var detector = this.detectorSections;
        var phi = this.phi;
        var phiUp = this.phiUpper;
        var phiDown = this.phiLower;
        var phiPi = Math.PI + phi;
        var phiUpPi = Math.PI + phiDown;
        var phiDownPi = Math.PI + phiUp;
        if (detector == "both" || detector == "right") {
            // Center of sector
            shapes.push(makeShape('line', 0, 0, (phi > this.phiToURCorner && phi < this.phiToULCorner) ? maxQy / Math.tan(phi) : maxQx,
                (phi > this.phiToURCorner && phi < this.phiToULCorner) ? maxQy : maxQx * Math.tan(phi)));
            // Top of sector
            shapes.push(makeShape('line', 0, 0, (phiUp > this.phiToURCorner && phiUp < this.phiToULCorner) ? maxQy / Math.tan(phiUp) : maxQx,
                (phiUp > this.phiToURCorner && phiUp < this.phiToULCorner) ? maxQy : maxQx * Math.tan(phiUp), "orange"));
            // Bottom of sector
            shapes.push(makeShape('line', 0, 0, (phiDown > this.phiToURCorner && phiDown < this.phiToULCorner) ? maxQy / Math.tan(phiDown) : maxQx,
                (phiDown > this.phiToURCorner && phiDown < this.phiToULCorner) ? maxQy : maxQx * Math.tan(phiDown), "orange"));
        }
        if (detector == "both" || detector == "left") {
            // Center of sector
            shapes.push(makeShape('line', 0, 0, (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner) ? minQy / Math.tan(phiPi) : minQx,
                (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner) ? minQy : minQx * Math.tan(phiPi)));
            // Bottom of sector
            shapes.push(makeShape('line', 0, 0, (phiUpPi > this.phiToLLCorner && phiUpPi < this.phiToLRCorner) ? minQy / Math.tan(phiUpPi) : minQx,
                (phiUpPi > this.phiToLLCorner && phiUpPi < this.phiToLRCorner) ? minQy : minQx * Math.tan(phiUpPi), "orange"));
            // Top of sector
            shapes.push(makeShape('line', 0, 0, (phiDownPi > this.phiToLLCorner && phiDownPi < this.phiToLRCorner) ? minQy / Math.tan(phiDownPi) : minQx,
                (phiDownPi > this.phiToLLCorner && phiDownPi < this.phiToLRCorner) ? minQy : minQx * Math.tan(phiDownPi), "orange"));
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
    constructor(params) {
        super(params);
    }

    calculateQ(theta) {
        return super.calculateQ(theta);
    }

    includePixel(xVal, yVal) {
        var correctedRadius = Math.sqrt(xVal * xVal + yVal * yVal);
        var dotProduct = (xVal * this.phiX + yVal * this.phiY) / correctedRadius;
        var dPhiPixel = Math.acos(dotProduct);
        var dPerpendicular = correctedRadius * Math.sin(dPhiPixel);
        var a = (dPerpendicular <= 0.5 * this.qWidth * this.pixelSize);
        var b = (this.detectorSections == "both");
        var c = (this.detectorSections == "left" && mirror);
        var d = (this.detectorSections == "right" && forward);
        return  a && (b || c || d);
    }

    createPlot() {
        var shapes = super.createPlot();
        if (detector == "both" || detector == "right") {
            // Center of rectangle
            shapes.push(makeShape('line', 0, 0, (phi > this.phiToURCorner && phi < this.phiToULCorner) ? maxQy / Math.tan(phi) : maxQx,
                (phi > this.phiToURCorner && phi < this.phiToULCorner) ? maxQy : maxQx * Math.tan(phi)));
            // Top of rectangle
            shapes.push(makeShape('line', 0, this.qWidth / 2, (phiUp > this.phiToURCorner && phiUp < this.phiToULCorner) ? maxQy / Math.tan(phiUp) : maxQx,
                (phiUp > this.phiToURCorner && phiUp < this.phiToULCorner) ? maxQy : maxQx * Math.tan(phiUp), "orange"));
            // Bottom of rectangle
            shapes.push(makeShape('line', 0, -1 * this.qWidth / 2, (phiDown > this.phiToURCorner && phiDown < this.phiToULCorner) ? maxQy / Math.tan(phiDown) : maxQx,
                (phiDown > this.phiToURCorner && phiDown < this.phiToULCorner) ? maxQy : maxQx * Math.tan(phiDown), "orange"));
        }
        if (detector == "both" || detector == "left") {
            // Center of rectangle
            shapes.push(makeShape('line', 0, 0, (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner) ? minQy / Math.tan(phiPi) : minQx,
                (phiPi > this.phiToLLCorner && phiPi < this.phiToLRCorner) ? minQy : minQx * Math.tan(phiPi)));
            // Bottom of sector
            shapes.push(makeShape('line', 0, this.qWidth / 2, (phiUpPi > this.phiToLLCorner && phiUpPi < this.phiToLRCorner) ? minQy / Math.tan(phiUpPi) : minQx,
                (phiUpPi > this.phiToLLCorner && phiUpPi < this.phiToLRCorner) ? minQy : minQx * Math.tan(phiUpPi), "orange"));
            // Top of sector
            shapes.push(makeShape('line', 0, 1 * this.qWidth / 2, (phiDownPi > this.phiToLLCorner && phiDownPi < this.phiToLRCorner) ? minQy / Math.tan(phiDownPi) : minQx,
                (phiDownPi > this.phiToLLCorner && phiDownPi < this.phiToLRCorner) ? minQy : minQx * Math.tan(phiDownPi), "orange"));
        }
        return shapes;
    }
}

/*
 * Circular averaging class
 */
class Elliptical extends Circular {
    constructor(params) {
        super(params);
    }

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
