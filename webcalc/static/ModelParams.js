const template = `
<div id="modelParams" v-if="Object.keys(model_params).length > 0" @set-model-persistence="loadPersistence">
 <h2>{{active_model}} Model Parameters:</h2>
  <ul class="parameter">
    <li v-for="(param, param_name) in model_params_local" :key="param_name">
      <label :for="active_model + '_' + param_name">{{param_name}}:</label>
      <input type="number" v-model.number="param.default" 
      :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
      :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
      @change="onChangeValue"
        />
    </li>
  </ul>
</div>
`

export default {
    props: {
        active_model: String,
        model_names: Array,
        model_params: Object,
    },
    watch: {
        model_params: {
          handler(newValue, oldValue) {
            this.model_params_local = newValue;
          }
        }
    },
    methods: {
        onChangeValue(event) {
          this.$emit('modelValueChange', this.model_params_local);
        },
        loadPersistence(params) {
            this.model_params_local = params;
        }
    },
    data: () => ({
        model_params_local: {},
    }),
    template: template,
}