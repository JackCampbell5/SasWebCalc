import AveragingParams from './AveragingParams.js';
import {default as ng7} from "./instruments/NG7SANS.js";
import {default as ngb30} from "./instruments/NGB30SANS.js";
import {default as vsans} from "./instruments/VSANS.js";
import {default as q_range} from "./instruments/UserDefinedQRange.js";
import {default as ngb10} from "./instruments/NGB10SANS.js";

const template = `
<header class="top">
<div class="section-header">
  <div class="section-header__main">
    <h1 class="section-header__title"><a href="https://www.nist.gov/ncnr">NIST Center for Neutron Research</a></h1>
  </div>
</div>
</header>
<header class="title">
<h1>SASCALC on the Web</h1>
</header>
<main>
<div class="centered-column" id="preamble">
  <div id="SASWEBCALC">
    <div class="instrument-section" title="Choose the instrument you plan to use.">
      <label for="instrumentSelector">Instrument: </label>
      <select id="instrumentSelector" v-model="active_instrument">
        <option v-for="(label, alias, index) in instruments" :key="alias" :value="alias">{{label}}</option>
      </select>
      <label id="modelLabel" for="model">Model: </label>
      <select id="model" v-model="active_model" @change="populateModelParams">
        <option v-for="model_name in model_names" :key="model_name" :value="model_name">{{model_name}}</option>
      </select>
      <label id="averagingTypeLabel" for="averagingType">Averaging Method: </label>
      <select id="averagingType" v-model="active_averaging_type">
        <option v-for="averaging in ['circular', 'sector', 'rectangular']" :key="averaging" :value="averaging">
          {{averaging}}</option>
        <!--
        <option value="annular">Annular</option>
        <option value="elliptical">Elliptical</option>
        -->
      </select>
    </div>
  </div>
  <div class="instrument-section" id="modelAndAveragingParams">
    <h3>Averaging and Model Parameters:</h3>
    <averaging-params ref="averaging_params" :active_averaging_type="active_averaging_type" @change="onChange"/>
    <div class="instrument-section" id="modelParams">
      <ul>
        <li v-for="(param, param_name) in model_params" :key="param_name">
          <label :for="active_model + '_' + param_name">{{param_name}}:</label>
          <input type="number" v-model.number="param.default" 
          :min="(param.lower_limit == '-inf') ? null : param.lower_limit"
          :max="(param.upper_limit == 'inf') ? null : param.upper_limit"
          @change="onModelParamChange"
            />
        </li>
      </ul>
    </div>
  </div>
  <div class="instrument-section" id="instrumentParams">
    <component v-if="active_instrument != ''" :is="active_instrument" @value-change="onInstrumentParamChange"/>
  </div>
</div>
</main>
`;

const instruments = {
  "q_range": "User-Defined Q-Range and Resolutions",
  //"ngb30": "NGB 30m SANS",
  "ng7": "NG7 SANS",
  //"ngb10": "NGB 10m SANS",
  //"vsans": "VSANS",
};

export default {
  components: {
    'averaging-params': AveragingParams,
    'q_range': q_range,
    "ngb30": ngb30,
    "ng7": ng7,
    "ngb10": ngb10,
    "vsans": vsans
  },
  data: () => ({
    active_instrument: "",
    active_averaging_type: "circular",
    active_model: "",
    model_names: [],
    model_params: {},
    instrument_params: {},
    instruments,
  }),
  methods: {
    async populateModelParams() {
      const fetch_result = await fetch(`/get/params/model/${this.active_model}`);
      this.model_params = await fetch_result.json();
      console.log(this.model_params);
    },
    async onModelParamChange() {
      let location = `/calculate/model/${this.active_model}`;
      let data = JSON.stringify(this.model_params);
      console.log(data);
      console.log(location);
      let results = await this.fetch_with_data(location, data);
      console.log(results);
    },
    async onInstrumentParamChange(params) {
      this.instrument_params = params;
      let location = `/calculate/instrument/${this.active_instrument}`;
      let data = this.instrument_params;
      let results = await this.fetch_with_data(location, data);
      console.log(results);
    },
    onChange(p) {
      // TODO: run calculations
      console.log('changed: ', p);
    },
    async fetch_with_data(location, data) {
      const fetch_result = await fetch(
          location,
          {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
      })
      return fetch_result.json();
    }
  },
  async beforeMount() {
    const fetch_result = await fetch("/get/models/");
    this.model_names = await fetch_result.json();
  },
  mounted() {
  },
  template
}

