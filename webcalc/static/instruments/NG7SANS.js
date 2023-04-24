const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="ng7_inputs">
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
      this.$emit('valueChange', this.instrument_params);
    },
    updateSecondaryElements(target) {
      if (target.id === "ng7GuideConfig") {
        this.updateApertureOptions(target);
      }
      else if (target.id === "ng7WavelengthSpread") {
        let range = this.wavelength_ranges[target.value];
        this.instrument_params['ng7WavelengthInput'].min = range[0];
        this.instrument_params['ng7WavelengthInput'].max = range[1];
      }
      else if (target.id === "ng7SampleAperture") {
        this.instrument_params['ng7CustomAperture'].hidden = !(target.value === 'Custom');
      }
      else if (target.id === "ng7SDDInputBox") {
        this.instrument_params['ng7SDDDefaults'].default = this.instrument_params['ng7SDDInputBox'].default;
      }
      else if (target.id === "ng7SDDDefaults") {
        this.instrument_params['ng7SDDInputBox'].default = this.instrument_params['ng7SDDDefaults'].default;
      }
    },
    updateApertureOptions(target) {
      // Update the allowed aperture values based on the number of guides selected
      let allApertureOptions = Object.values(document.getElementById("ng7SourceAperture").options);
      let guideApertureOptions = this.source_apertures[target.value];
      for (let aperture of allApertureOptions) {
        let toggle = !guideApertureOptions.includes(aperture.value.toString());
        // If the aperture is a possible value, enable it and set it to the existing value
        aperture.disabled = toggle;
        aperture.hidden = toggle;
        if (!toggle) {
          this.instrument_params['ng7SourceAperture'].default = aperture.value;
        }
      }
    }
  },
  computed: {
    item_in_category: function () {
      return Object.keys(this.instrument_params)
        .filter(key => this.instrument_params[key].category === this.active_category).
        reduce((obj, key) => {
          obj[key] = this.instrument_params[key];
        return obj;
        }, {});
    },
  },
  data() {
    return {
      active_category: "",
      categories: {
        "ng7Sample": {display_name: 'Sample Area Settings'},
        "ng7Wavelength": {display_name: 'Wavelength Settings'},
        "ng7Collimation": {display_name: 'Collimation Settings'},
        "ng7Detector": {display_name: 'Detector Settings'},
        "ng7QRange": {display_name: 'Calculated Q Range'},
      },
      source_apertures: {
        0: ['1.43', '2.54', '3.81'],
        1: ['5.08'],
        2: ['5.08'],
        3: ['5.08'],
        4: ['5.08'],
        5: ['5.08'],
        6: ['5.08'],
        7: ['5.08'],
        8: ['5.08'],
        'LENS': ['1.43'],
      },
      wavelength_ranges: {
        9.7: ['6.5', '20.0'],
        13.9: ['4.8', '20.0'],
        15: ['4.5', '20.0'],
        22.1: ['4.0', '20.0']
      },
      instrument_params: {
        'ng7SampleTable': {
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
          default: 6.0,
          min: 4.8,
          max: 20.0,
          type: "number",
          unit: 'nm;',
          category: 'ng7Wavelength',
        },
        'ng7WavelengthSpread': {
          name: 'Wavelength Spread',
          default: 13.9,
          type: "select",
          category: 'ng7Wavelength',
          unit: '',
          //TODO Question: where is 11.5 and why is 15 here
          options: [9.7, 13.9, 15, 22.1],
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
          options: [0, 1, 2, 3, 4, 5, 6, 7, 8, 'LENS'],
        },
        'ng7SourceAperture': {
          name: 'Source Aperture',
          default: 1.43,
          type: "select",
          unit: 'cm',
          category: 'ng7Collimation',
          options: [1.43, 2.54, 3.81, 5.08],
        },
        'ng7SampleAperture': {
          name: 'Sample Aperture',
          default: 0.500,
          type: "select",
          unit: 'inch',
          category: 'ng7Collimation',
          options: [0.125, 0.25, 0.375, 0.125, 0.500, 0.625, 0.75, 0.875, 1.00, 'Custom'],
        },
        'ng7CustomAperture': {
          name: 'Aperture Diameter',
          default: 13,
          type: "number",
          unit: 'mm',
          category: 'ng7Collimation',
          hidden: true,
        },
        'ng7SSD': {
          name: 'Source-To-Sample Distance',
          default: 1627,
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
          default: 100,
          type: "range",
          category: 'ng7Detector',
          range_id: 'ng7SDDDefaultRange',
          unit: '',
          lower_limit: 90,
          upper_limit: 1532,
          options: [100, 400, 1300, 1530],
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
          range_id: 'ng7OffsetDefaultRange',
          unit: '',
          lower_limit: 0,
          upper_limit: 25,
          options: [0, 5, 10, 15, 20, 25],
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
          unit: "Å;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
        'ng7MaximumQ': {
          name: 'Maximum Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
        'ng7MaximumVerticalQ': {
          name: 'Maximum Vertical Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
        'ng7MaximumHorizontalQ': {
          name: 'Maximum Horizontal Q',
          default: '',
          type: "number",
          unit: "Å;<sup>-1</sup>",
          category: 'ng7QRange',
          readonly: true,
        },
      }
    }
  },
  mounted(){
    this.$emit('valueChange', this.instrument_params);
  },
  watch: {
    pythonParams: function (value){
      let instName = "ng7";

      for (const name in value){
        this.instrument_params[instName+name].default = value[name];
      }
    }

  },
  template: template
}