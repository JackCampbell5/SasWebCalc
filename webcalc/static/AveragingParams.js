import { averagingInputs } from './constants.js';

const template = `
   <div id="averagingParams" v-if="visibleParams.length > 0">
      <h2>{{active_averaging_type}} Parameters:</h2>
      <ul class="parameter">
        <li v-if="visibleParams.includes('phi')">
           <label for="phi">Orientation Angle (&#176;): </label>
           <input v-model="averagingParams.phi" type="number" min="0" max="90" id="phi" title="" />
        </li>
        <li v-if="visibleParams.includes('dPhi')">
           <label for="dPhi">Azimuthal Range (&#176;): </label>
           <input v-model="averagingParams.dPhi" type="number" min="0" max="45" id="dPhi" title="" />
        </li>
        <li v-if="visibleParams.includes('detectorSections')">
           <label for="detectorSections">Detector Sections: </label>
           <select v-model="averagingParams.detectorHalves" id="detectorSections">
              <option value="both" selected>Entire Detector</option>
              <option value="left" selected>Left Only</option>
              <option value="right" selected>Right Only</option>
           </select>
        </li>
        <li v-if="visibleParams.includes('qCenter')">
           <label for="qCenter">Q Center of Annulus (&#8491;<sup>-1</sup>): </label>
           <input v-model="averagingParams.qCenter" type="number" min="0.00" max="1.0" step="0.01" id="qCenter"
              title="" />
        </li>
        <li v-if="visibleParams.includes('qWidth')">
           <label for="qWidth">Q Width (&#8491;<sup>-1</sup>): </label>
           <input v-model="averagingParams.qWidth" type="number" min="0.00" max="1.0" step="0.01" id="qWidth" title="" />
        </li>
        <li v-if="visibleParams.includes('qHeight')">
           <label for="qHeight">Q Height (&#8491;<sup>-1</sup>): </label>
           <input v-model="averagingParams.qHeight" type="number" min="0.00" max="1.0" step="0.01" id="qHeight" title="" />
        </li>
        <li v-if="visibleParams.includes('aspectRatio')">
           <label for="aspectRatio">Ellipse Aspect Ratio: </label>
           <input v-model="averagingParams.aspectRatio" type="number" min="0" max="1" step="0.1" id="aspectRatio"
              title="" />
        </li>
      </ul>
   </div>
`;

export default {
  props: {
    active_averaging_type: String,
    data_1d: Object,
    data_2d: Object,
  },
  data: () => ({
    averagingParams: {
      phi: 0,
      dPhi: 0,
      detectorHalves: "both",
      qCenter: 0.1,
      qWidth: 0.05,
      qHeight: 0.02,
      aspectRatio: 1.0,
    },
    shapes: [],
  }),
  computed: {
    visibleParams() {
      return (this.active_averaging_type == null) ? [] : averagingInputs[this.active_averaging_type];
    }
  },
  watch: {
    averagingParams: {
      handler(newValue, oldValue) {
        this.makeAveragingShapes();
        this.$emit('changeAveParams', this.averagingParams);
        this.$emit('changeShapes', this.shapes);
      },
      deep: true
    }
  },
  methods: {
    makeAveragingShapes() {
      // Reset shapes so only current shape(s) visible
      this.shapes = [];
      // Get all parameters to be used by any slicer drawer
      let type = this.active_averaging_type;
      let qCenter = parseFloat(this.averagingParams['qCenter']);
      let qWidth = parseFloat(this.averagingParams['qWidth']);
      let qHeight = parseFloat(this.averagingParams['qHeight']);
      let phi = parseFloat(this.averagingParams['phi']) * Math.PI / 180;
      let dPhi = parseFloat(this.averagingParams['dPhi']) * Math.PI / 180;
      let halves = this.averagingParams['detectorHalves'];
      let aspectRatio = parseFloat(this.averagingParams['aspectRatio']);
      let maxQx = 1.0;
      let minQx = -1.0;
      let maxQy = 1.0;
      let minQy = -1.0;
      if (this.data_2d != null) {
          maxQx = this.getMax(this.data_2d['qxValues']);
          minQx = this.getMin(this.data_2d['qxValues']);
          maxQy = this.getMax(this.data_2d['qyValues']);
          minQy = this.getMin(this.data_2d['qyValues']);
      }
      switch (type) {
          default: case 'Circular':
            // No shapes needed for a circular or empty slicer
            break;
          case 'Sector':
            let phiUp = phi + dPhi;
            let phiDown = phi - dPhi;
            let phiToURCorner = Math.atan(maxQy / maxQx);
            let phiToULCorner = Math.atan(maxQy / minQx) + Math.PI;
            let phiToLLCorner = Math.atan(minQy / minQx) + Math.PI;
            let phiToLRCorner = Math.atan(minQy / maxQx) + 2 * Math.PI;
            if (halves === "both" || halves === "right") {
                this.shapes.push(this.makeShape('line', 0, 0, (phi > phiToURCorner && phi < phiToULCorner) ? maxQy / Math.tan(phi) : maxQx,
                    (phi > phiToURCorner && phi < phiToULCorner) ? maxQy : maxQx * Math.tan(phi)));
                this.shapes.push(this.makeShape('line', 0, 0, (phiUp > phiToURCorner && phiUp < phiToULCorner) ? maxQy / Math.tan(phiUp) : maxQx,
                    (phiUp > phiToURCorner && phiUp < phiToULCorner) ? maxQy : maxQx * Math.tan(phiUp), "orange"));
                this.shapes.push(this.makeShape('line', 0, 0, (phiDown > phiToURCorner && phiDown < phiToULCorner) ? maxQy / Math.tan(phiDown) : maxQx,
                    (phiDown > phiToURCorner && phiDown < phiToULCorner) ? maxQy : maxQx * Math.tan(phiDown), "orange"));
            }
            if (halves === "both" || halves === "left") {
                this.shapes.push(this.makeShape('line', 0, 0, (phi > phiToLLCorner && phi < phiToLRCorner) ? minQy / Math.tan(phi) : minQx,
                    (phi > phiToLLCorner && phi < phiToLRCorner) ? minQy : minQx * Math.tan(phi)));
                this.shapes.push(this.makeShape('line', 0, 0, (phiUp > phiToLLCorner && phiUp < phiToLRCorner) ? minQy / Math.tan(phiUp) : minQx,
                    (phiUp > phiToLLCorner && phiUp < phiToLRCorner) ? minQy : minQx * Math.tan(phiUp), "orange"));
                this.shapes.push(this.makeShape('line', 0, 0, (phiDown > phiToLLCorner && phiDown < phiToLRCorner) ? minQy / Math.tan(phiDown) : minQx,
                    (phiDown > phiToLLCorner && phiDown < phiToLRCorner) ? minQy : minQx * Math.tan(phiDown), "orange"));
            }
            break;
          case 'Annular':
            let innerQ = Math.max(qCenter - qWidth, 0);
            let outerQ = qCenter + qWidth;
            this.shapes.push(this.makeShape('circle', -1 * qCenter, -1 * qCenter, qCenter, qCenter, "white"));
            this.shapes.push(this.makeShape('circle', -1 * innerQ, -1 * innerQ, innerQ, innerQ, "orange"));
            this.shapes.push(this.makeShape('circle', -1 * outerQ, -1 * outerQ, outerQ, outerQ, "orange"));
            break;
          case 'Rectangular':
            if (halves === "left") {
                this.shapes.push(this.makeShape('rect', -1 * qWidth / 2, qHeight / 2, 0, -1 * qHeight / 2, "orange"));
            } else if (halves === "right") {
                this.shapes.push(this.makeShape('rect', 0, qHeight / 2, qWidth / 2, -1 * qHeight / 2, "orange"));
            } else {
                this.shapes.push(this.makeShape('rect', -1 * qWidth / 2, -1 * qHeight / 2, qWidth / 2, qHeight / 2, "orange"));
            }
            break;
          case 'Elliptical':
            let side = aspectRatio * maxQy;
            let start = 0;
            let end = 2 * Math.PI;
            let steps = 100;
            if (halves === "left") { start = Math.PI / 2; end = 3 * Math.PI / 2; steps = 50; }
            if (halves === "right") { start = -1 * Math.PI / 2; end = Math.PI / 2; steps = 50; }
            this.shapes.push(this.makeSVGPath(this.makeEllipseArc(0, 0, side, maxQy, start, end, phi, steps, false)));
            break;
      }
    },
    /*
    * Return a dictionary that defines a line object in plot.ly
    */
    makeShape(shape, x0, y0, x1, y1, color = "black") {
        return {
            type: shape,
            xref: 'x',
            yref: 'y',
            x0: x0,
            y0: y0,
            x1: x1,
            y1: y1,
            line: {
                color: color,
            }
        };
    },
    /*
     * Return a dictionary that defines a path-like object in plot.ly
     */
    makeSVGPath(path, color = "black") {
        return {
            type: 'path',
            path: path,
            line: {
                color: color,
            }
        };
    },
    /*
     * Return a path-like object that represents an oriented ellipse-like shape
     */
    makeEllipseArc(xCenter = 0, yCenter = 0, a = 1, b = 1, startAngle = 0, endAngle = 2 * Math.PI, orientationAngle = 0, N = 100, closed = false) {
        // FIXME: orientationAngle needs to work properly
        let x = [];
        let y = [];
        let t = this.makeArr(startAngle, endAngle, N);
        for (let i = 0; i < t.length; i++) {
            x[i] = xCenter + a * Math.cos(t[i] + orientationAngle);
            y[i] = yCenter + b * Math.sin(t[i] + orientationAngle);
        }
        let path = 'M ' + x[0] + ', ' + y[0];
        for (let k = 1; k < t.length; k++) {
            path += ' L' + x[k] + ', ' + y[k];
        }
        if (closed) {
            path += ' Z';
        }
        return path
    },
    /*
     * Create a filled array from startValue to stopValue with cardinality points in between
     */
    makeArr(startValue, stopValue, cardinality) {
        let arr = [];
        let step = (stopValue - startValue) / (cardinality - 1);
        for (let i = 0; i < cardinality; i++) {
            arr.push(startValue + (step * i));
        }
        return arr;
    },
    getMax(array) {
        return Math.max(...array.map(e => Array.isArray(e) ? this.getMax(e) : e))
    },
    getMin(array) {
        return Math.min(...array.map(e => Array.isArray(e) ? this.getMin(e) : e))
    }
  },
  template: template
}
