import AveragingParams from './AveragingParams.js';
import {default as ng7} from "./instruments/NG7SANS.js";
import {default as ngb30} from "./instruments/NGB30SANS.js";
import {default as vsans} from "./instruments/VSANS.js";
import {default as qrange} from "./instruments/UserDefinedQRange.js";
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
  <div class="instrument-section">
    <component :is="instrument_components[active_instrument]" :title="instruments[active_instrument]" @change="onInstrumentParamChange" />
  </div>
</div>
</main>
`;

const instruments = {
  "qrange": "User-Defined Q-Range and Resolutions",
  "ngb30": "NGB 30m SANS",
  "ng7": "NG7 SANS",
  "ngb10": "NGB 10m SANS",
  "vsans": "VSANS",
};

const instrument_components = { qrange, ngb30, ng7, ngb10, vsans };

export default {
  components: {
    'averaging-params': AveragingParams
  },
  data: () => ({
    active_instrument: "",
    active_averaging_type: "circular",
    active_model: "",
    model_names: [],
    model_params: {},
    instruments,
    instrument_components
  }),
  methods: {
    async populateModelParams() {
      const fetch_result = await fetch(`/getparams/${this.active_model}`);
      this.model_params = await fetch_result.json();
    },
    onModelParamChange() {
      console.log(JSON.stringify(this.model_params, null, 2));
    },
    onInstrumentParamChange() {
      // do stuff
    },
    onChange(p) {
      console.log('changed: ', p);
    }
  },
  async mounted() {
    const fetch_result = await fetch("/getmodels/");
    this.model_names = await fetch_result.json();
  }, 
  template
}

