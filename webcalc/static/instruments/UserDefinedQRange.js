const template = `
<div class="instrument_params">
  <h3>{{title}}</h3>
  <div id="q_range_inputs">
  <!-- FIXME: The values aren't being set when changed... -->
    <div class="params" v-for="(param, param_name) in params" :key="param_name">
        <label :for="param_name">{{param.name}}:&nbsp;</label>
        <select v-if="param.type == 'select'" v-model="param" :id="'q_range_' + param_name"
            :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
            :max="(param.upper_limit == 'inf') ? null : param.upper_limit">
            <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
        </select>
        <input v-else :id="param_name" class="fixed-width-input"
            :type="param.type" v-model="param" v-model.value="param.default" :value="param.value"
            :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
            :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
        />
        <span v-if="param.unit != ''">&nbsp;{{param.unit}}</span>
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
      q_min_vertical: {
        name: 'Q Min Vertical',
        default: -0.3,
        value: -0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      q_max_vertical: {
        name: 'Q Max Vertical',
        default: 0.3,
        value: 0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      q_min_horizontal: {
        name: 'Q Min Horizontal',
        default: -0.3,
        value: -0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      q_max_horizontal: {
        name: 'Q Max Horizontal',
        default: 0.3,
        value: 0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      dq: {
        name: 'Q Resolution',
        default: 10.0,
        value: 10.0,
        type: "number",
        min: 0.0,
        max: 'inf',
        unit: '%',
      },
      points: {
        name: 'Number of 1D points',
        default: 50,
        value: 50,
        type: "number",
        min: 0.0,
        max: 1000,
        unit: '',
      },
      point_spacing: {
        name: 'Point Spacing',
        default: "lin",
        value: "lin",
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