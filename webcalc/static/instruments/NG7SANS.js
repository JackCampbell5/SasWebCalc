const template = `
<div class="instrument_params">
  <h3>{{title}}</h3>
  <div id="ng7_inputs">
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

      }

    }
  },
  template: template
}