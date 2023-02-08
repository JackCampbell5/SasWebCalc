import AveragingParams from './AveragingParams.js';
import {default as ng7} from "./instruments/NG7SANS.js";
import {default as ngb30} from "./instruments/NGB30SANS.js";
import {default as vsans} from "./instruments/VSANS.js";
import {default as q_range} from "./instruments/UserDefinedQRange.js";
import {default as ngb10} from "./instruments/NGB10SANS.js";
import {default as plotting} from "./Plotting.js";
import {default as model} from "./ModelParams.js";

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
        <option v-for="averaging in averaging_types" :key="averaging" :value="averaging">
          {{averaging}}</option>
      </select>
    </div>
  </div>
  <div class="instrument-section" id="modelAndAveragingParams">
    <averaging-params ref="averaging_params" :active_averaging_type="active_averaging_type" :data_1d="data_1d"
        :data_2d="data_2d" @change-shapes="onShapeChange" @change-ave-params="onAveragingChange"/>
    <model-params ref="model" :active_model="active_model" :model_names="model_names" :model_params="model_params"
        @model-value-change="onModelParamChange" />
  </div>
  <div class="instrument-section" id="instrumentParams">
    <component v-if="active_instrument != ''" :is="active_instrument" :title="instruments[active_instrument]"
        @value-change="onInstrumentParamChange"/>
  </div>
  <plotting ref="plotting" :data_1d="data_1d" :data_2d="data_2d" :shapes="shapes" />
</div>
</main>
`;

const instruments = {
  "q_range": "User-Defined Q-Range and Resolutions",
  "ngb30": "NGB 30m SANS",
  "ng7": "NG7 SANS",
  "ngb10": "NGB 10m SANS",
  //"vsans": "VSANS",
};

export default {
  components: {
    'averaging-params': AveragingParams,
    'model-params': model,
    'plotting': plotting,
    'q_range': q_range,
    "ngb30": ngb30,
    "ng7": ng7,
    "ngb10": ngb10,
    "vsans": vsans
  },
  data: () => ({
    active_instrument: "",
    active_averaging_type: "Circular",
    averaging_types: {
      'circular': 'Circular',
      'sector: ': 'Sector',
      'rectangular': 'Rectangular',
      'annular': 'Annular',
      'elliptical': 'Elliptical',
    },
    active_model: "",
    model_names: [],
    model_params: {},
    instrument_params: {},
    data_1d: {},
    data_2d: {},
    averaging_params: {},
    shapes: [],
    instruments,
  }),
  methods: {
    async populateModelParams() {
      const fetch_result = await fetch(`/get/params/model/${this.active_model}`);
      this.model_params = await fetch_result.json();
    },
    async onModelParamChange() {
      let location = `/calculate/model/${this.active_model}`;
      await this.onChange();
    },
    async onInstrumentParamChange(params) {
      this.instrument_params = params;
      await this.onChange();
    },
    async onAveragingChange(params) {
      this.averaging_params = params;
      await this.onChange();
    },
    onShapeChange(shapes) {
      this.shapes = shapes;
    },
    async onChange() {
      let location = `/calculate/`;
      let data = JSON.stringify({
        'instrument': this.instrument_params,
        'model': this.model_params,
        'averaging': this.averaging_params,
      });
      console.log(data);
      let results = await this.fetch_with_data(location, data);
      console.log(results);

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
    // TODO: Remove this once everything is working
    this.data_1d = {
      qValues: [0.0001, 0.001, 0.01, 0.1],
      intensity: [1000, 100, 10, 1],
    };
    this.data_2d = {
        qxValues: [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]],
        qyValues: [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]],
        intensity2D: [[0, 0, 0],[0, 1130, 0],[0, 0, 0]],
    };
  },
  template: template,
}

