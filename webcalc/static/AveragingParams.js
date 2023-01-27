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
    active_averaging_type: String
  },
  data: () => ({
    averagingParams: {
      phi: 0,
      dPhi: 0,
      detectorHalves: "both",
      qCenter: 0.1,
      qWidth: 0.05,
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
        this.$emit('change', newValue);
      },
      deep: true
    }
  },
  methods: {
    makeAveragingShapes() {
      this.shapes = [];
      let type = this.active_averaging_type;
      switch (type) {
          default: case 'Circular':
            // No shapes needed for a circular or empty slicer
            break;
          case 'Sector':
            // TODO: Write this
            break;
          case 'Annular':
            let qCenter = parseFloat(this.averagingParams['qCenter']);
            let qWidth = parseFloat(this.averagingParams['qWidth']);
            let innerQ = qCenter - qWidth;
            let outerQ = qCenter + qWidth;
            this.shapes.push(this.makeShape('circle', -1 * qCenter, -1 * qCenter, qCenter, qCenter, "white"));
            this.shapes.push(this.makeShape('circle', -1 * innerQ, -1 * innerQ, innerQ, innerQ, "orange"));
            this.shapes.push(this.makeShape('circle', -1 * outerQ, -1 * outerQ, outerQ, outerQ, "orange"));
            break;
          case 'Rectangular':
            // TODO: Write this
            break;
          case 'Elliptical':
            // TODO: Write this
            break;
      }
      this.shapes = shapes;
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
}
  },
  template: template
}
