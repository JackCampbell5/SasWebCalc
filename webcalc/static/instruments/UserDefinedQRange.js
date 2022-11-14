const template = `
<div class="instrument_params">
  <h3>{{title}}</h3>
  <div>
    <div class="params" v-for="(param, param_name) in params" :key="param_name">
        <label :for="'q_range_' + param_name">{{param_name}}:</label>
        <select v-if="param.type == 'select'" v-model.number="param.default" :id="'q_range_' + param_name"
            :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
            :max="(param.upper_limit == 'inf') ? null : param.upper_limit">
            <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
        </select>
        <input v-else :id="'q_range_' + param_name" class="fixed-width-input"
            :type="param.type" v-model.value="param.default" 
            :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
            :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
        />
        <span v-if="param.unit != ''">{{param.unit}}</span>
    </div>
  </div>
</div>
`

// TODO: Resolutions for Pinhole vs. Slit vs. others...
export default {
  props: {
    title: String
  },
  data: () => ({
    params: {
      q_min: {
        default: 0.0,
        type: "number",
        min: 0.0,
        max: 2.0,
        unit: 'Å',
      },
      q_max: {
        default: 1.0,
        type: "number",
        min: 0.0,
        max: 2.0,
        unit: 'Å',
      },
      dq: {
        default: 10.0,
        type: "number",
        min: 0.0,
        max: 'inf',
        unit: '%',
      },
      points: {
        default: 50,
        type: "number",
        min: 0.0,
        max: 1000,
        unit: '',
      },
      point_spacing: {
        default: "lin",
        type: "select",
        options: [
            'lin',
            'log'
        ],
        unit: '',
      },
    }
  }),
  template: template
}