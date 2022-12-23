const template = `
<div class="instrument_params">
  <h3>{{title}}</h3>
  <div id="q_range_inputs">
    <div class="param" v-for="(param, key) in instrument_params" :key="key">
        <label :for="key">{{param.name}}:&nbsp;</label>
        <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" @change="onChangeValue">
            <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
        </select>
        <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
            :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
            :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
            @input="onChangeValue"/>
        <span v-if="param.unit != ''">&nbsp;{{param.unit}}</span>
    </div>
  </div>
</div>
`

export default {
  props: {
    title: String,
    instrument_params: {type: Object, default: {}},
  },
  methods: {
   onChangeValue (event) {
       this.$emit('valueChange', this.instrument_params);
   }
  },
  data() {
    return {
      instrument_params: {
        'q_min_vertical': {
          name: 'Q Min Vertical',
          default: -0.3,
          type: "number",
          min: -2.0,
          max: 2.0,
          unit: 'Å',
        },
        'q_max_vertical': {
          name: 'Q Max Vertical',
          default: 0.3,
          type: "number",
          min: -2.0,
          max: 2.0,
          unit: 'Å',
        },
        'q_min_horizontal': {
          name: 'Q Min Horizontal',
          default: -0.3,
          type: "number",
          min: -2.0,
          max: 2.0,
          unit: 'Å',
        },
        'q_max_horizontal': {
          name: 'Q Max Horizontal',
          default: 0.3,
          type: "number",
          min: -2.0,
          max: 2.0,
          unit: 'Å',
        },
        'q_min': {
          name: 'Q Minimum',
          default: 0.01,
          type: "number",
          min: -2.0,
          max: 2.0,
          unit: 'Å',
        },
        'dq': {
          name: 'Q Resolution',
          default: 10.0,
          type: "number",
          min: 0.0,
          max: 'inf',
          unit: '%',
        },
        'points': {
          name: 'Number of 1D points',
          default: 50,
          type: "number",
          min: 0.0,
          max: 1000,
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
  template: template,
}