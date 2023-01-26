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
      let shapes = [];
      let params = this.averagingParams;
      let used_params = {};
      let type = this.active_averaging_type;
      let expected_params = averagingInputs[type];
      for (let param in params) {
          if (params[param] in expected_params) {
              used_params[param] = params[param];
          }
      }
      switch (type) {
          default: case 'Circular':
              // No shapes needed for a circular or empty slicer
              break;
          case 'Sector':
              // TODO: Write this
              break;
          case 'Annular':
              // TODO: Write this
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
  },
  template: template
}

