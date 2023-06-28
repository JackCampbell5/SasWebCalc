const template = `
<div class="instrument_params">
  <h2>{{title}}</h2>
  <div id="q_range_inputs">
    <div class="param, instrument-section" v-for="(param, key) in instrument_params_local" :key="key" >
        <label :for="key">{{param.name}}:&nbsp;</label>
        <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" @change="onChangeValue">
            <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
        </select>
        <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
            :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
            :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
            :step="(param.step!== undefined) ? param.step : null"
            @input="onChangeValue"/>
        <span v-if="param.unit != ''">&nbsp;{{param.unit}}</span>
    </div>
  </div>
</div>
`

export default {
  props: {
    title: String,
  },
  methods: {
   onChangeValue (event) {
       this.$emit('valueChange', this.instrument_params_local);
   }
  },
  data() {
    return {
      instrument_params_local: {
        'q_min_vertical': {
          name: 'Q Min Vertical',
          default: -0.3,
          type: "number",
          lower_limit: -2.0,
          upper_limit: 2.0,
          unit: 'Å',
          step: 0.1,
        },
        'q_max_vertical': {
          name: 'Q Max Vertical',
          default: 0.3,
          type: "number",
          lower_limit: -2.0,
          upper_limit: 2.0,
          unit: 'Å',
          step: 0.1,
        },
        'q_min_horizontal': {
          name: 'Q Min Horizontal',
          default: -0.3,
          type: "number",
          lower_limit: -2.0,
          upper_limit: 2.0,
          unit: 'Å',
          step: 0.1,
        },
        'q_max_horizontal': {
          name: 'Q Max Horizontal',
          default: 0.3,
          type: "number",
          lower_limit: -2.0,
          upper_limit: 2.0,
          unit: 'Å',
          step: 0.1,
        },
        'q_min': {
          name: 'Q Minimum',
          default: 0.01,
          type: "number",
          lower_limit: -2.0,
          upper_limit: 2.0,
          unit: 'Å',
          step: 0.01,
        },
        'dq': {
          name: 'Q Resolution',
          default: 10.0,
          type: "number",
          lower_limit: 0.0,
          upper_limit: 'inf',
          unit: '%',
        },
        'points': {
          name: 'Number of 1D points',
          default: 50,
          type: "number",
          lower_limit: 0.0,
          upper_limit: 1000,
          unit: '',
        },
        'point_spacing': {
          name: 'Point Spacing',
          default: "lin",
          type: "select",
          options: [
            'lin',
            'log'
          ],
          unit: '',
        },
      },
    }
  },
  mounted(){
    this.$emit('valueChange', this.instrument_params_local);
  },
  template: template,
}