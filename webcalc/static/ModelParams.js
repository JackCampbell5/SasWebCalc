const template = `
<div id="modelParams" v-if="Object.keys(model_params).length > 0" @model-changed="populateModelParams">
 <h2>{{active_model}} Model Parameters:</h2>
  <ul class="parameter">
    <li v-for="(param, param_name) in model_params" :key="param_name">
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
        model_names: Array,
        model_params: {type: Object, default: {}},
    },
    methods: {
        onChangeValue(event) {
          this.$emit('modelValueChange', this.model_params);
        },
        async populateModelParams() {
          const fetch_result = await fetch(`/get/params/model/${this.active_model}`);
          this.model_params = await fetch_result.json();
        },
        async onModelParamChange() {
          let location = `/calculate/model/${this.active_model}`;
          let data = JSON.stringify(this.model_params);
          let results = await this.fetch_with_data(location, data);
        },
        async beforeMount() {
            const fetch_result = await fetch("/get/models/");
            this.model_names = await fetch_result.json();
            this.$emit('modelNamesList', this.model_names);
        },
    },
    data: () => ({
        active_model: "",
        model_names: [],
        model_params: {},
    }),
    template: template,
}