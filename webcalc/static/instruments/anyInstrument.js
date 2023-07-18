const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="_inputs">
    <div v-for="(params,category_name) in instrument_params_local" :id="category_name" :key="category_name" class="instrument-section">
      <div v-if="category_name != 'hidden'">
      <span v-if="params.name !=' '"><h3>{{params.name}}:</h3></span>
      <ul class="parameter">
        <li v-for="(param, key) in params" :key="key" class="parameter" v-show="!param.hidden">
          <div v-if="key != 'name'">
          <label :for="key" v-if="param.name != ' '">{{param.name}}<span v-if="param.unit != ''"> (<span v-html="param.unit"></span>)</span>: </label>
          <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" 
              :disabled="param.readonly" @change="onChangeValue">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
          </select>
          <input type = "checkbox" v-else-if="param.type == 'checkbox'" v-model.string="param.default" :id="key" 
              :disabled="param.readonly" @change="onChangeValue">
          <span v-else-if="param.type == 'range'">
            <input type="range" v-model.string="param.default" :disabled="param.readonly" :id="key" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :step="(param.step!== undefined) ? param.step : null"
              :list="param.range_id" @change="onChangeValue" />
            <datalist :id="param.range_id">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
            </datalist>
          </span>
          <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :step="(param.step!== undefined) ? param.step : null"
              :disabled="param.readonly"  @input="onChangeValue"/>
        </div>
        </li>
      </ul>
      </div>
    </div>
  </div>
</div>
`

export default {
  props: {
    title: String,
    instrument_params_local: {},
  },
  data: () => ({
    source_apertures: {},
    wavelength_ranges:{},
    secondary_elements:{},
    first_run: true,
    run: true,
  }),
  methods: {
    onChangeValue(event) {
      this.run= true;
      this.updateSecondaryElements(event.target);
      if (!event.target.disabled && this.run) {
        this.$emit('valueChange', this.instrument_params_local);
      }
    },
    updateSecondaryElements(target) {
      if(!("hidden" in this.instrument_params_local)){
        return;
      }
      if (target.value === '' || "hidden"){
        this.run = false;
        return;
      }
      if(this.first_run && "hidden" in this.instrument_params_local){
        this.source_apertures = this.instrument_params_local["hidden"]["source_apertures"];
        this.wavelength_ranges = this.instrument_params_local["hidden"]["wavelength_ranges"];
        this.secondary_elements = this.instrument_params_local["hidden"]["secondary_elements"];
        this.first_run = false;
      }else if (!("hidden" in this.instrument_params_local)){
        return;
      }
      if (Object.keys(this.secondary_elements).includes(target.id)){
        let update_dict = this.secondary_elements[target.id];
        this.instrument_params_local[update_dict["cat1"]][update_dict["name1"]].default =
            this.instrument_params_local[update_dict["cat2"]][update_dict["name2"]].default;
      }
      else if (target.id === "guideConfig") {
        this.updateApertureOptions(target);
      }
      else if (target.id === "wavelengthSpread") {
        let range = this.wavelength_ranges[target.value];
        this.instrument_params_local['Wavelength']['wavelengthInput'].lower_limit = range[0];
        this.instrument_params_local['Wavelength']['wavelengthInput'].upper_limit = range[1];

        if (this.instrument_params_local['Wavelength']['wavelengthInput'].default<range[0]){
          this.instrument_params_local['Wavelength']['wavelengthInput'].default = range[0];
        }else if(this.instrument_params_local['Wavelength']['wavelengthInput'].default>range[1]){
          this.instrument_params_local['Wavelength']['wavelengthInput'].default = range[1];
        }
      }
      else if (target.id === "sampleAperture") {
        this.instrument_params_local['Collimation']['customAperture'].hidden = !(target.value === 'Custom');
      }

    },
    updateApertureOptions(target) {
      // Update the allowed aperture values based on the number of guides selected
      let allApertureOptions = Object.values(document.getElementById("sourceAperture").options);
      let guideApertureOptions = this.source_apertures[target.value];
      for (let aperture of allApertureOptions) {
        let toggle = !guideApertureOptions.includes(parseFloat(aperture.value));
        // If the aperture is a possible value, enable it and set it to the existing value
        aperture.disabled = toggle;
        aperture.hidden = toggle;
        if (!toggle) {
          this.instrument_params_local['Collimation']['sourceAperture'].default = aperture.value;
        }
      }
    }
  },
  watch: {
    title: function (value){
      this.first_run = true;
    }

  },

  mounted(){
    this.$emit('valueChange', this.instrument_params_local);
  },
  template: template
}