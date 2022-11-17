const template = `
<div class="instrument_params">
  <h3>{{title}}</h3>
  <div id="q_range_inputs">
  <!-- FIXME: The values aren't being set when changed... -->
    <div class="params" v-for="(param, index) in params" :key="param.key">
        <label :for="param.key">{{param.name}}:&nbsp;</label>
        <select v-if="param.type == 'select'" v-model="params[index].default" :id="param.key">
            <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
        </select>
        <input v-else v-model="params[index].default" :id="param.key" class="fixed-width-input" :type="param.type"
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
    params: [
       {
        key: 'q_min_vertical',
        name: 'Q Min Vertical',
        default: -0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      {
        key: 'q_max_vertical',
        name: 'Q Max Vertical',
        default: 0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      {
        key: 'q_min_horizontal',
        name: 'Q Min Horizontal',
        default: -0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      {
        key: 'q_max_horizontal',
        name: 'Q Max Horizontal',
        default: 0.3,
        type: "number",
        min: -2.0,
        max: 2.0,
        unit: 'Å',
      },
      {
        key: 'dq',
        name: 'Q Resolution',
        default: 10.0,
        type: "number",
        min: 0.0,
        max: 'inf',
        unit: '%',
      },
      {
        key: 'points',
        name: 'Number of 1D points',
        default: 50,
        type: "number",
        min: 0.0,
        max: 1000,
        unit: '',
      },
      {
        key: 'point_spacing',
        name: 'Point Spacing',
        default: "lin",
        type: "select",
        options: [
          'lin',
          'log'
        ],
        unit: '',
      },
    ]
  }),
  template: template
}