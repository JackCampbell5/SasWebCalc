class Slicer{
    constructor(params = {}) {
        // TODO make new slicer constructor
    }//End Slicer constructor
}// End Slicer Class

class Circular extends Slicer{
    constructor(params) {
        super(params);
    }// End Circular constructor
}// End Circular class

class Sector extends Slicer {
     constructor(params) {
        super(params);
    }// End Sector constructor

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

}// End Sector class

class Rectangular extends Slicer {
    constructor(params) {
        super(params);
    }// End rectangular constructor

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

}// End rectangular class


class Elliptical extends Circular {
    constructor(params) {
        super(params);
    }// End Elliptical constructor
}// End Elliptical