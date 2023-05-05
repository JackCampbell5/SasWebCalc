const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="ngb30_inputs">
    <div v-for="(category, cat_key) in categories" :id="cat_key" :key="cat_key" class="instrument-section" :set="active_category = cat_key">
      <h3>{{category.display_name}}:</h3>
      <ul class="parameter">
        <li v-for="(param, key) in item_in_category" :key="key" class="parameter" v-show="!param.hidden">
          <label :for="key" v-if="param.name != ''">{{param.name}}<span v-if="param.unit != ''"> (<span v-html="param.unit"></span>)</span>: </label>
          <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" 
              :disabled="param.readonly" @change="onChangeValue">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
          </select>
          <span v-else-if="param.type == 'range'">
            <input type="range" v-model.string="param.default" :disabled="param.readonly" :id="key" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :list="param.range_id" @change="onChangeValue" />
            <datalist :id="param.range_id">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
            </datalist>
          </span>
          <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :disabled="param.readonly"  @input="onChangeValue"/>
        </li>
      </ul>
    </div>
  </div>
</div>
`

export default {
  props: {
    title: String,
    pythonParams: {},
  },
  methods: {
    onChangeValue(event) {
      this.updateSecondaryElements(event.target);
      this.$emit('valueChange', this.instrument_params_local);
    },
    updateSecondaryElements(target) {
      if (target.id === "ngb30GuideConfig") {
        this.updateApertureOptions(target);
      }
      else if (target.id === "ngb30WavelengthSpread") {
        let range = this.wavelength_ranges[target.value];
        this.instrument_params_local['ngb30WavelengthInput'].min = range[0];
        this.instrument_params_local['ngb30WavelengthInput'].max = range[1];
      }
      else if (target.id === "ngb30SampleAperture") {
        this.instrument_params_local['ngb30CustomAperture'].hidden = !(target.value === 'Custom');
      }
      else if (target.id === "ngb30SDDInputBox") {
        this.instrument_params_local['ngb30SDDDefaults'].default = this.instrument_params_local['ngb30SDDInputBox'].default;
      }
      else if (target.id === "ngb30SDDDefaults") {
        this.instrument_params_local['ngb30SDDInputBox'].default = this.instrument_params_local['ngb30SDDDefaults'].default;
      }
      else if (target.id === "ngb30OffsetInputBox") {
        this.instrument_params_local['ngb30OffsetDefaults'].default = this.instrument_params_local['ngb30OffsetInputBox'].default;
      }
      else if (target.id === "ngb30OffsetDefaults") {
        this.instrument_params_local['ngb30OffsetInputBox'].default = this.instrument_params_local['ngb30OffsetDefaults'].default;
      }
    },
    updateApertureOptions(target) {
      // Update the allowed aperture values based on the number of guides selected
      let allApertureOptions = Object.values(document.getElementById("ngb30SourceAperture").options);
      let guideApertureOptions = this.source_apertures[target.value];
      for (let aperture of allApertureOptions) {
        let toggle = !guideApertureOptions.includes(aperture.value.toString());
        // If the aperture is a possible value, enable it and set it to the existing value
        aperture.disabled = toggle;
        aperture.hidden = toggle;
        if (!toggle) {
          this.instrument_params_local['ngb30SourceAperture'].default = aperture.value;
        }
      }
    }
  },
  computed: {
    item_in_category: function () {
      return Object.keys(this.instrument_params_local)
        .filter(key => this.instrument_params_local[key].category === this.active_category).
        reduce((obj, key) => {
          obj[key] = this.instrument_params_local[key];
        return obj;
        }, {});
    },
  },
  data() {
    return {
      active_category: "",
      categories: {
        "ngb30Sample": {display_name: 'Sample Area Settings'},
        "ngb30Wavelength": {display_name: 'Wavelength Settings'},
        "ngb30Collimation": {display_name: 'Collimation Settings'},
        "ngb30Detector": {display_name: 'Detector Settings'},
        "ngb30QRange": {display_name: 'Calculated Q Range'},
      },
      source_apertures: {
        0: [1.43, 2.54, 3.81],
        1: [5.08],
        2: [5.08],
        3: [5.08],
        4: [5.08],
        5: [5.08],
        6: [5.08],
        7: [5.08, 2.5, 0.95],
        8: [5.08],
        'LENS': [1.43],
      },
      wavelength_ranges: {
        10.9: ['6.0', '20.0'],
        12.1: ['5.5', '20.0'],
        13.8: ['4.5', '20.0'],
        16.8: ['3.0', '20.0'],
        25.6: ['3.0', '20.0']
      },
      instrument_params_local: {
        'ngb30SampleTable': {
          name: 'Sample Table',
          default: "Chamber",
          type: "select",
          options: [
            'Chamber',
            'Huber'
          ],
          unit: '',
          category: 'ngb30Sample',
        },
        'ngb30WavelengthInput': {
          name: 'Wavelength',
          default: 6.0,
          min: 3.0,
          max: 20.0,
          type: "number",
          unit: 'nm;',
          category: 'ngb30Wavelength',
        },
        'ngb30WavelengthSpread': {
          name: 'Wavelength Spread',
          default: 13.8,
          type: "select",
          category: 'ngb30Wavelength',
          unit: '',
          options: [10.9, 12.1, 13.8, 16.8, 25.6],
        },
        'ngb30BeamFlux': {
          name: 'Beam Flux',
          default: '',
          type: "number",
          unit: 'n cm<sup>-2</sup> s<sup>-1</sup>',
          category: 'ngb30Wavelength',
          readonly: true,
        },
        'ngb30FigureOfMerit': {
          name: 'Figure of merit',
          default: '',
          type: "number",
          unit: '',
          category: 'ngb30Wavelength',
          readonly: true,
        },
        'ngb30Attenuators': {
          name: 'Attenuators',
          default: '',
          type: "number",
          unit: '',
          category: 'ngb30Wavelength',
          readonly: true,
        },
        'ngb30AttenuationFactor': {
          name: 'Attenuation Factor',
          default: '',
          type: "number",
          unit: '',
          category: 'ngb30Wavelength',
          readonly: true,
        },
        'ngb30GuideConfig': {
          name: 'Guides',
          default: 0,
          type: "select",
          category: 'ngb30Collimation',
          unit: '',
          options: [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS'],
        },
        'ngb30SourceAperture': {
          name: 'Source Aperture',
          default: 1.43,
          type: "select",
          unit: 'cm',
          category: 'ngb30Collimation',
          options: [0.95, 1.43, 2.50, 2.54, 3.81, 5.08],
        },
        'ngb30SampleAperture': {
          name: 'Sample Aperture',
          default: 0.500,
          type: "select",
          unit: 'inch',
          category: 'ngb30Collimation',
          options: [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom'],
        },
        'ngb30CustomAperture': {
          name: 'Aperture Diameter',
          default: 13,
          type: "number",
          unit: 'mm',
          category: 'ngb30Collimation',
          hidden: true,
        },
        'ngb30SSD': {
          name: 'Source-To-Sample Distance',
          default: 1627,
          type: "number",
          unit: 'cm',
          category: 'ngb30Collimation',
          readonly: true,
        },
        'ngb30SDDInputBox': {
          name: 'Detector Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ngb30Detector',
        },
        'ngb30SDDDefaults': {
          name: '',
          default: 133,
          type: "range",
          category: 'ngb30Detector',
          range_id: 'ngb30SDDDefaultRange',
          unit: '',
          lower_limit: 130,
          upper_limit: 1330,
          options: [133, 400, 1300],
        },
        'ngb30OffsetInputBox': {
          name: 'Detector Offset',
          default: 0,
          type: "number",
          unit: 'cm',
          category: 'ngb30Detector',
        },
        'ngb30OffsetDefaults': {
          name: '',
          default: 0,
          type: "range",
          category: 'ngb30Detector',
          range_id: 'ngb30OffsetDefaultRange',
          unit: '',
          lower_limit: 0,
          upper_limit: 25,
          options: [0, 5, 10, 15, 20, 25],
        },
        'ngb30SDD': {
          name: 'Sample-To-Detector Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ngb30Detector',
          readonly: true,
        },
        'ngb30BeamDiameter': {
          name: 'Beam Diameter',
          default: '',
          type: "number",
          unit: "inch",
          category: 'ngb30Detector',
          readonly: true,
        },
        'ngb30BeamStopSize': {
          name: 'Beam Stop Diameter',
          default: '',
          type: "number",
          unit: "inch",
          category: 'ngb30Detector',
          readonly: true,
        },
        'ngb30MinimumQ': {
          name: 'Minimum Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb30QRange',
          readonly: true,
        },
        'ngb30MaximumQ': {
          name: 'Maximum Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb30QRange',
          readonly: true,
        },
        'ngb30MaximumVerticalQ': {
          name: 'Maximum Vertical Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb30QRange',
          readonly: true,
        },
        'ngb30MaximumHorizontalQ': {
          name: 'Maximum Horizontal Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb30QRange',
          readonly: true,
        },
      }
    }
  },
  mounted(){
    this.$emit('valueChange', this.instrument_params_local);
  },
   watch: {
    pythonParams: function (value){
      let instName = "ngb30";

      for (const name in value){
        this.instrument_params_local[instName+name].default = value;
      }
    }

  },
  template: template
}