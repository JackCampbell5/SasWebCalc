const template = `
<div class="instrument_params">
  <h2>{{title}} Instrumental Parameters</h2>
  <div id="ng7_inputs">
    <div v-for="(category, cat_key) in categories" :id="cat_key" :key="cat_key" class="instrument-section" >
      <h3>{{category.display_name}}:</h3>
      <div class="instrument-section">
      <span class="parameter" v-for="(param, key) in instrument_params" :key="key">
        <span v-if="param.category == cat_key" :style="(param.hidden) ? 'display:none' : ''">
          <label :for="key" v-if="param.name != ''">{{param.name}}<span v-if="param.unit != ''"> (<span v-html="param.unit"></span>)</span>: </label>
          <select v-if="param.type == 'select'" v-model.string="param.default" :id="key" 
              :disabled="param.readonly" @change="onChangeValue">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
          </select>
          <span v-else-if="param.type == 'range'">
            <input type="range" v-model.string="param.default" :disabled="param.readonly"
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :list="key" @change="param.changeMethod" />
            <datalist :id="param.range_id">
              <option v-for="option in param.options" :key="option" :value="option">{{option}}</option>
            </datalist>
          </span>
          <input v-else type="number" v-model.number="param.default" :id="key" class="fixed-width-input" 
              :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
              :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
              :disabled="param.readonly"  @input="onChangeValue"/>
         </span>
      </span>
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