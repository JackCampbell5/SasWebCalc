const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="ngb10_inputs">
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
      if (!event.target.disabled) {
        this.$emit('valueChange', this.instrument_params_local);
      }
    },
    updateSecondaryElements(target) {
      if (target.id === "ngb10GuideConfig") {
        this.updateApertureOptions(target);
      }
      else if (target.id === "ngb10WavelengthSpread") {
        let range = this.wavelength_ranges[target.value];
        this.instrument_params_local['ngb10WavelengthInput'].min = range[0];
        this.instrument_params_local['ngb10WavelengthInput'].max = range[1];
      }
      else if (target.id === "ngb10SampleAperture") {
        this.instrument_params_local['ngb10CustomAperture'].hidden = !(target.value === 'Custom');
      }
      else if (target.id === "ngb10SDDInputBox") {
        this.instrument_params_local['ngb10SDDDefaults'].default = this.instrument_params_local['ngb10SDDInputBox'].default;
      }
      else if (target.id === "ngb10SDDDefaults") {
        this.instrument_params_local['ngb10SDDInputBox'].default = this.instrument_params_local['ngb10SDDDefaults'].default;
      }
      else if (target.id === "ngb10OffsetInputBox") {
        this.instrument_params_local['ngb10OffsetDefaults'].default = this.instrument_params_local['ngb10OffsetInputBox'].default;
      }
      else if (target.id === "ngb10OffsetDefaults") {
        this.instrument_params_local['ngb10OffsetInputBox'].default = this.instrument_params_local['ngb10OffsetDefaults'].default;
      }
    },
    updateApertureOptions(target) {
      // Update the allowed aperture values based on the number of guides selected
      let allApertureOptions = Object.values(document.getElementById("ngb10SourceAperture").options);
      let guideApertureOptions = this.source_apertures[target.value];
      for (let aperture of allApertureOptions) {
        let toggle = !guideApertureOptions.includes(aperture.value.toString());
        // If the aperture is a possible value, enable it and set it to the existing value
        aperture.disabled = toggle;
        aperture.hidden = toggle;
        if (!toggle) {
          this.instrument_params_local['ngb10SourceAperture'].default = aperture.value;
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
        "ngb10Wavelength": {display_name: 'Wavelength Settings'},
        "ngb10Collimation": {display_name: 'Collimation Settings'},
        "ngb10Detector": {display_name: 'Detector Settings'},
        "ngb10QRange": {display_name: 'Calculated Q Range'},
      },
      source_apertures: {
        0: [1.3, 2.5, 3.8],
        1: [5],
        2: [5]
      },
      wavelength_ranges: {
        9.2: ['5.5', '20.0'],
        12: ['4.0', '20.0'],
        14: ['3.0', '20.0'],
        25: ['3.0', '20.0']
      },
      instrument_params_local: {
        'ngb10BeamStopSizes': {
          options: [2.54, 3.81, 5.08, 7.62]
        },
        'ngb10WavelengthInput': {
          name: 'Wavelength',
          default: 6.0,
          min: 3.0,
          max: 20.0,
          type: "number",
          unit: 'nm;',
          category: 'ngb10Wavelength',
        },
        'ngb10WavelengthSpread': {
          name: 'Wavelength Spread',
          default: 12,
          type: "select",
          category: 'ngb10Wavelength',
          unit: '',
          options: [9.2, 12, 14, 25],
        },
        'ngb10BeamFlux': {
          name: 'Beam Flux',
          default: '',
          type: "number",
          unit: 'n cm<sup>-2</sup> s<sup>-1</sup>',
          category: 'ngb10Wavelength',
          readonly: true,
        },
        'ngb10FigureOfMerit': {
          name: 'Figure of merit',
          default: '',
          type: "number",
          unit: '',
          category: 'ngb10Wavelength',
          readonly: true,
        },
        'ngb10Attenuators': {
          name: 'Attenuators',
          default: '',
          type: "number",
          unit: '',
          category: 'ngb10Wavelength',
          readonly: true,
        },
        'ngb10AttenuationFactor': {
          name: 'Attenuation Factor',
          default: '',
          type: "number",
          unit: '',
          category: 'ngb10Wavelength',
          readonly: true,
        },
        'ngb10GuideConfig': {
          name: 'Guides',
          default: 0,
          type: "select",
          category: 'ngb10Collimation',
          unit: '',
          options: [0, 1, 2],
        },
        'ngb10SourceAperture': {
          name: 'Source Aperture',
          default: 1.3,
          type: "select",
          unit: 'cm',
          category: 'ngb10Collimation',
          options: [1.3, 2.5, 3.8, 5],
        },
        'ngb10SampleAperture': {
          name: 'Sample Aperture',
          default: 0.500,
          type: "select",
          unit: 'inch',
          category: 'ngb10Collimation',
          options: [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom'],
        },
        'ngb10CustomAperture': {
          name: 'Aperture Diameter',
          default: 13,
          type: "number",
          unit: 'mm',
          category: 'ngb10Collimation',
          hidden: true,
        },
        'ngb10SSD': {
          name: 'Source-To-Sample Distance',
          default: 513,
          type: "number",
          unit: 'cm',
          category: 'ngb10Collimation',
          readonly: true,
        },
        'ngb10SDDInputBox': {
          name: 'Detector Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ngb10Detector',
        },
        'ngb10SDDDefaults': {
          name: '',
          default: 100,
          type: "range",
          category: 'ngb10Detector',
          range_id: 'ngb10SDDDefaultRange',
          unit: '',
          lower_limit: 77,
          upper_limit: 415,
          options: [100, 400],
        },
        'ngb10SDD': {
          name: 'Sample-To-Detector Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ngb10Detector',
          readonly: true,
        },
        'ngb10BeamDiameter': {
          name: 'Beam Diameter',
          default: '',
          type: "number",
          unit: "cm",
          category: 'ngb10Detector',
          readonly: true,
        },
        'ngb10BeamStopSize': {
          name: 'Beam Stop Diameter',
          default: '',
          type: "number",
          unit: "cm",
          category: 'ngb10Detector',
          readonly: true,
        },
        'ngb10MinimumQ': {
          name: 'Minimum Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb10QRange',
          readonly: true,
        },
        'ngb10MaximumQ': {
          name: 'Maximum Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb10QRange',
          readonly: true,
        },
        'ngb10MaximumVerticalQ': {
          name: 'Maximum Vertical Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb10QRange',
          readonly: true,
        },
        'ngb10MaximumHorizontalQ': {
          name: 'Maximum Horizontal Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ngb10QRange',
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
      let instName = "ngb10";

      for (const name in value){
        this.instrument_params_local[instName+name].default = value[name];
      }
    }

  },
  template: template
}