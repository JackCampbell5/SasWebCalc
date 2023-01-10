const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="ng7_inputs">
    <div v-for="(category, cat_key) in categories" :id="cat_key" :key="cat_key" class="instrument-section" >
      <h3>{{category.display_name}}:</h3>
      <div class="instrument-section">
      <span v-for="(param, key) in instrument_params" :key="key">
        <span class="parameter" v-if="param.category == cat_key" :style="(param.hidden) ? 'display:none' : ''">
          <label :for="key" v-if="param.name != ''">{{param.name}}<span v-if="param.unit != ''"> (<span v-html="param.unit"></span>)</span>: </label>
          <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" 
              :disabled="param.readonly" @change="onChangeValue">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
          </select>
          <span v-else-if="param.type == 'range'">
            <input type="range" v-model.string="param.default" :disabled="param.readonly"
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :list="key" @change="param.changeMethod" />
            <datalist :id="param.range_id">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
            </datalist>
          </span>
          <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :disabled="param.readonly"  @input="onChangeValue"/>
         </span>
      </span>
      </div>
  </div>
</div>
`

export default {
  props: {
    title: String,
    instrument_params: {type: Object, default: {}},
    categories: {type: Object, default: {}},
  },
  methods: {
   onChangeValue (event) {
       this.$emit('valueChange', this.instrument_params);
   }
  },
  data() {
    return {
      title: "NG7 SANS",
      categories: {
        "ng7Sample": {display_name: 'Sample Area Settings'},
        "ng7Wavelength": {display_name: 'Wavelength Settings'},
        "ng7Collimation": {display_name: 'Collimation Settings'},
        "ng7Detector": {display_name: 'Detector Settings'},
        "ng7QRange": {display_name: 'Calculated Q Range'},
      },
      instrument_params: {
        'ng7_sample_table': {
          name: 'Sample Table',
          default: "Chamber",
          type: "select",
          options: [
            'Chamber',
            'Huber'
          ],
          unit: '',
          category: 'ng7Sample',
        },
        'ng7WavelengthInput': {
          name: 'Wavelength',
          default: '',
          type: "number",
          unit: '&#8491;',
          category: 'ng7Wavelength',
        },
        'ng7WavelengthSpread': {
          name: 'Wavelength Spread',
          default: 11.5,
          type: "select",
          category: 'ng7Wavelength',
          unit: '',
          options: [9.3, 11.5, 13.9, 22.1]
        },
        'ng7BeamFlux': {
          name: 'Beam Flux',
          default: '',
          type: "number",
          unit: 'n cm<sup>-2</sup> s<sup>-1</sup>',
          category: 'ng7Wavelength',
          readonly: true,
        },
        'ng7FigureOfMerit': {
          name: 'Figure of merit',
          default: '',
          type: "number",
          unit: '',
          category: 'ng7Wavelength',
          readonly: true,
        },
        'ng7Attenuators': {
          name: 'Attenuators',
          default: '',
          type: "number",
          unit: '',
          category: 'ng7Wavelength',
          readonly: true,
        },
        'ng7AttenuationFactor': {
          name: 'Attenuation Factor',
          default: '',
          type: "number",
          unit: '',
          category: 'ng7Wavelength',
          readonly: true,
        },
        'ng7GuideConfig': {
          name: 'Guides',
          default: 0,
          type: "select",
          category: 'ng7Collimation',
          unit: '',
          options: [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS']
        },
        'ng7SourceAperture': {
          name: 'Source Aperture',
          default: 1.43,
          type: "select",
          unit: 'cm',
          category: 'ng7Collimation',
          options: [1.43, 2.54, 3.81, 5.08]
        },
        'ng7SampleAperture': {
          name: 'Sample Aperture',
          default: 0.500,
          type: "select",
          unit: 'inch',
          category: 'ng7Collimation',
          options: [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom']
        },
        'ng7CustomAperture': {
          name: 'Aperture Diameter',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ng7Collimation',
          hidden: true,
        },
        'ng7SSD': {
          name: 'Source-To-Sample Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ng7Collimation',
          readonly: true,
        },
        'ng7SDDInputBox': {
          name: 'Detector Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ng7Detector',
        },
        'ng7SDDDefaults': {
          name: '',
          default: 0,
          type: "range",
          category: 'ng7Detector',
          range_id: 'ng7SDDDefaults',
          unit: '',
          lower_limit: 90,
          upper_limit: 1532,
          options: [100, 400, 1300, 1530]
        },
        'ng7OffsetInputBox': {
          name: 'Detector Offset',
          default: 0,
          type: "number",
          unit: 'cm',
          category: 'ng7Detector',
        },
        'ng7OffsetDefaults': {
          name: '',
          default: 0,
          type: "range",
          category: 'ng7Detector',
          unit: '',
          lower_limit: 0,
          upper_limit: 25,
          options: [0, 5, 10, 15, 20, 25]
        },
        'ng7SDD': {
          name: 'Sample-To-Detector Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ng7Detector',
          readonly: true,
        },
        'ng7BeamDiameter': {
          name: 'Beam Diameter',
          default: '',
          type: "number",
          unit: "inch",
          category: 'ng7Detector',
          readonly: true,
        },
        'ng7BeamStopSize': {
          name: 'Beam Stop Diameter',
          default: '',
          type: "number",
          unit: "inch",
          category: 'ng7Detector',
          readonly: true,
        },
        'ng7MinimumQ': {
          name: 'Minimum Q',
          default: '',
          type: "number",
          unit: "&#8491;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
        'ng7MaximumQ': {
          name: 'Maximum Q',
          default: '',
          type: "number",
          unit: "&#8491;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
        'ng7MaximumVerticalQ': {
          name: 'Maximum Vertical Q',
          default: '',
          type: "number",
          unit: "&#8491;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
        'ng7MaximumHorizontalQ': {
          name: 'Maximum Horizontal Q',
          default: '',
          type: "number",
          unit: "&#8491;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
      }

    }
  },
  template: template
}