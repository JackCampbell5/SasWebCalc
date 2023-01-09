const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="ng7_inputs">
    <div v-for="(category, cat_key) in categories" :id="cat_key" :key="cat_key" class="instrument-section" >
      <h3>{{category.display_name}}:</h3>
      <div class="parameter" v-for="(param, key) in instrument_params" :key="key">
        <span v-if="param.category == cat_key">
          <label :for="key">{{param.name}}:&nbsp;</label>
          <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" @change="onChangeValue">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
          </select>
          <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              @input="onChangeValue"/>
          <span v-if="param.unit != ''">&nbsp;{{param.unit}}</span>
         </span>
      </div>
     </div>
  </div>
</div>
`

export default {
  props: {
    title: String,
    instrument_params: {type: Object, default: {}},
    categories: {type: Object, default: {}},
  },
  methods: {
   onChangeValue (event) {
       this.$emit('valueChange', this.instrument_params);
   }
  },
  data() {
    return {
      title: "NG7 SANS",
      categories: {
        "ng7Sample": {
          display_name: 'Sample Space'
        },
      },
      instrument_params: {
        'ng7_sample_table': {
          name: 'Sample Table',
          default: "Chamber",
          type: "select",
          options: [
            'Chamber',
            'Huber'
          ],
          unit: '',
          category: 'ng7Sample',
        },
        'ng7_sdd': {
          name: 'Sample-To-Detector-Distance',
          default: 100,
          type: "number",
          unit: 'cm',
          category: 'ng7Detector',
        },
      }

    }
  },
  template: template
}