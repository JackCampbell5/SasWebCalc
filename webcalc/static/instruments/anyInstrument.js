const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="_inputs">
    <div v-for="(params,key) in instrument_params_local" :id="key" :key="key" class="instrument-section">
      <h3>{{params.name}}:</h3>
      <ul class="parameter">
        <li v-for="(param, key) in params" :key="key" class="parameter" v-show="!param.hidden">
          <div v-if="key != 'name'">
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
        </div>
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
    instrument_params_local: {},
    source_apertures: {},
    wavelength_ranges:{},
  },
  methods: {
    onChangeValue(event) {
      this.updateSecondaryElements(event.target);
      if (!event.target.disabled) {
        this.$emit('valueChange', this.instrument_params_local);
      }
    },
    updateSecondaryElements(target) {
      if (target.id === "GuideConfig") {
        this.updateApertureOptions(target);
      }
      else if (target.id === "WavelengthSpread") {
        let range = this.wavelength_ranges[target.value];
        this.instrument_params_local['WavelengthInput'].min = range[0];
        this.instrument_params_local['WavelengthInput'].max = range[1];
      }
      else if (target.id === "SampleAperture") {
        this.instrument_params_local['CustomAperture'].hidden = !(target.value === 'Custom');
      }
      else if (target.id === "SDDInputBox") {
        this.instrument_params_local['SDDDefaults'].default = this.instrument_params_local['SDDInputBox'].default;
      }
      else if (target.id === "SDDDefaults") {
        this.instrument_params_local['SDDInputBox'].default = this.instrument_params_local['SDDDefaults'].default;
      }
      else if (target.id === "OffsetInputBox") {
        this.instrument_params_local['OffsetDefaults'].default = this.instrument_params_local['OffsetInputBox'].default;
      }
      else if (target.id === "OffsetDefaults") {
        this.instrument_params_local['OffsetInputBox'].default = this.instrument_params_local['OffsetDefaults'].default;
      }
    },
    updateApertureOptions(target) {
      // Update the allowed aperture values based on the number of guides selected
      let allApertureOptions = Object.values(document.getElementById("SourceAperture").options);
      let guideApertureOptions = this.source_apertures[target.value];
      for (let aperture of allApertureOptions) {
        let toggle = !guideApertureOptions.includes(parseFloat(aperture.value));
        // If the aperture is a possible value, enable it and set it to the existing value
        aperture.disabled = toggle;
        aperture.hidden = toggle;
        if (!toggle) {
          this.instrument_params_local['SourceAperture'].default = aperture.value;
        }
      }
    }
  },
  mounted(){
    this.$emit('valueChange', this.instrument_params_local);
  },
  watch: {
    pythonParams: function (value){
      console.log("Updating Python Params")
      for (const type in value){
        for (const param in value[type]) {
          this.instrument_params_local[type][param].default = value[type][param];
        }//End type for loop
        }// End value or loop
    }

  },
  template: template
}