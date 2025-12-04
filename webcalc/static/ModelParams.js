const template = `
<div id="modelParams" v-if="Object.keys(model_params).length > 0">
 <h2>{{active_model}} Model Parameters:</h2>
  <ul class="parameter">
    <li v-for="(param, param_name) in model_params_local" :key="param_name">
      <label :for="active_model + '_' + param_name">{{param_name}}:</label>
      <input type="number" v-model.number="param.default"
      :class="(param.warn === true) ? 'warn' : ''"
      :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
      :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
      @change="onChangeValue"
      :id="active_model + '_' + param_name"
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
            this.model_run = true;
            this.checkInputsAreValid();
            if (this.model_run) {
                this.$emit('modelValueChange', this.model_params_local);
            }
        },
        checkInputsAreValid() {
          for (const [key, param] of Object.entries(this.model_params_local)) {
              if (param.default === "") {
                this.model_run = false;
                param["warn"] = true;
              }
              else {
                param["warn"] = false;
              }
              this.model_params_local[key] = param
          }
        },
    },
    data: () => ({
        model_params_local: {},
        model_run: true,
    }),
    template: template,
}