import AveragingParams from './AveragingParams.js';
import {default as vsans} from "./instruments/VSANS.js";
import {default as anyInstrument} from "./instruments/anyInstrument.js";
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
 <div class = "section_subheader">
    <a href="https://gitlab.nist.gov/gitlab/jkrzywon/saswebcalc/-/issues/new"  target="_blank">
      <button class="top-level-button" title="Bug submission tool">!</button>
    </a>
      <button class="top-level-button" title="Docs Access" @click="docsDisplay">?</button>

</div>
</header>
<main>
<div class="centered-column" id="preamble">
  <div id="SASWEBCALC">
    <div class="instrument-section" title="Choose the instrument you plan to use.">
      <label for="instrumentSelector">Instrument: </label>
      <select id="instrumentSelector" v-model="active_instrument_change" @change = "getParamsInstrument">
        <option v-for="(label, alias, index) in instruments" :key="alias" :value="alias">{{label}}</option>
      </select>
      <label id="modelLabel" for="model">Model: </label>
      <select id="model" v-model="active_model" @change="onModelChange">
        <option v-for="model_name in model_names" :key="model_name" :value="model_name">{{model_name}}</option>
      </select>
      <label id="structureLabel" for="model">Structure Factor: </label>
      <select id="structure" v-model="active_structure" @change="onStructureChange">
        <option v-for="structure_name in structure_names" :key="structure_name" :value="structure_name">{{structure_name}}</option>
      </select>
      <label id="averagingTypeLabel" for="averagingType">Averaging Method: </label>
      <select id="averagingType" v-model="active_averaging_type">
        <option v-for="averaging in averaging_types" :key="averaging" :value="averaging">
          {{averaging}}</option>
      </select>
    </div>
  </div>
  <div class="documentation" v-show="documentation_shown">
  <iframe src="/docs/index.html" title="SasWebCalc Documentation"  width="100%" height="500" style="border:1px solid black;"></iframe>
  </div>
  <plotting ref="plotting" :data_1d="data_1d" :data_2d="data_2d" :shapes="shapes" :calculating_shown="calculating_shown"/>
 
  <div class="instrument-section" id="modelAndAveragingParams">
    <averaging-params ref="averaging_params" :active_averaging_type="active_averaging_type" :data_1d="data_1d"
        :data_2d="data_2d" @change-shapes="onShapeChange" @change-ave-params="onAveragingChange"/>
    <model-params ref="model" :active_model="active_model" :model_names="model_names" :model_params="model_params"
        @model-value-change="onModelParamChange" />
  </div>
  <div class="instrument-section" id="instrumentParams">
    <anyInstrument v-if="active_instrument != ''" :is="active_instrument" :title="instruments[active_instrument]"
        :instrument_params_local="instrument_params" @value-change="onInstrumentParamChange"/>
  </div>
</div>
</main>
`;

export default {
  components: {
    'averaging-params': AveragingParams,
    'model-params': model,
    'plotting': plotting,
    "vsans": vsans,
    "anyInstrument": anyInstrument,
  },
  data: () => ({
    active_instrument: "",
    active_instrument_change: "",
    active_averaging_type: "Circular",
    averaging_types: {
      'circular': 'Circular',
      // 'sector: ': 'Sector',
      // 'rectangular': 'Rectangular',
      // 'annular': 'Annular',
      // 'elliptical': 'Elliptical',
    },
    active_model: "",
    active_structure: "",
    structure_names: [],
    structure_names_original: [],
    multiplicity_models: [],
    model_names: [],
    model_params: {},
    instrument_params: {},
    data_1d: {},
    data_2d: {},
    frozen: [],
    offset: false,
    averaging_params: {},
    shapes: [],
    instruments: {},
    documentation_shown: false,
    calculating_shown: false,
    log: "",
  }),
  methods: {
    async getParamsInstrument(){
      const fetch_result = await this.fetch_without_data(`/get/params/instrument/${this.active_instrument_change}`);
      this.instrument_params =  await fetch_result.json();
      this.active_instrument = this.active_instrument_change
      await this.onChange();
    },
    async populateModelParams() {
      if(this.active_model !== ""){
        let model_name = this.active_structure !== this.structure_names[0] ? this.active_model+'@'+this.active_structure :  this.active_model
        const fetch_result = await this.fetch_without_data(`/get/params/model/${model_name}`);
        this.model_params = await fetch_result.json();
      }//End if statement
      },
    async onModelChange() {
        if (this.structure_names_original.includes(this.active_model)||this.multiplicity_models.includes(this.active_model)) {
          this.structure_names = [this.structure_names_original[0]];
          this.active_structure = this.structure_names[0];
        }else {
          this.structure_names = this.structure_names_original;
        }// End fi statement for if the structure is missing and needed
        await this.populateModelParams();
      await this.onChange();
    },
    async onStructureChange() {
      await this.populateModelParams()
      await this.onChange();
    },
    async onModelParamChange() {
      let location = `/update/params/`;
        this.persist();
        let data = JSON.stringify({
          'model': this.active_model,
          'model_params': this.model_params,
        });
        let results = await this.fetch_with_data(location, data);
        this.model_params = results;

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
    onFreeze(frozen) {
      this.frozen = frozen;
    },
    onOffset(offset) {
      this.offset = offset;
    },
    async onChange() {
      //Does not run the function if the instrument or model is blank
      // This is so when the python objects are created they have the correct data
      if(this.active_instrument !== "" && this.active_model !== "") {
        this.calculating_shown = true;
        let location = `/calculate/`;
        this.persist();
        let data = JSON.stringify({
          'instrument': this.active_instrument,
          'instrument_params': this.instrument_params,
          'model': this.active_model,
          'model_params': this.model_params,
          'structure_factor': this.active_structure,
          'averaging_type': this.active_averaging_type,
          'averaging_params': this.averaging_params,
        });
        let results = await this.fetch_with_data(location, data);
        if("user_inaccessible" in results){
          let value = results["user_inaccessible"];
          for (const type in value){
            for (const param in value[type]) {
              this.instrument_params[type][param].default = value[type][param];
            }//End type for loop
          }// End value or loop
        }
        this.data_1d = {qValues:results["qValues"],intensity:results["fSubs"]};
        this.data_2d = {qxValues:results["qxValues"],qyValues:results["qyValues"],intensity2D: results["intensity2D"]};
        this.calculating_shown = false;

      }//End if statement to check instrument existence

    },
    async fetch_without_data(location) {
      this.logging(location);
      return await fetch(location);
    },
    async fetch_with_data(location, data) {
      this.logging(location);
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
    },
    logging(location) {
      let elemStr = "status";
      let today = new Date();
      let dateTime = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate()+' '+today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
      let newElem = document.createElement("p");
      newElem.textContent = `${dateTime}: Sending updated values to ${location}`;
      let elem = document.getElementById(elemStr);
      if (elem != null) {
        elem.insertBefore(newElem, elem.firstChild);
      }
    },
    persist() {
      /*
      Store the current values into active memory to be recalled if the page is refreshed.
       */
      localStorage.setItem("active_instrument", this.active_instrument);
      localStorage.setItem("active_averaging_type", this.active_averaging_type);
      localStorage.setItem("active_model", this.active_model);
      localStorage.setItem("active_structure",this.active_structure);
      localStorage.setItem(this.active_model + "_model_params", JSON.stringify(this.model_params));
      localStorage.setItem(this.active_instrument + "_instrument_params", JSON.stringify(this.instrument_params));
      localStorage.setItem(this.active_averaging_type + "_averaging_params", JSON.stringify(this.averaging_params));
      localStorage.setItem("frozen", JSON.stringify(this.frozen));
      localStorage.setItem("offset", this.offset);
    },
    loadPersistentState() {
      this.active_instrument = localStorage.getItem('active_instrument') || "";
      this.active_averaging_type = localStorage.getItem("active_averaging_type") || "Circular";
      this.active_model = localStorage.getItem("active_model") || "";
    },
    docsDisplay(){
      this.documentation_shown = !this.documentation_shown
    }
  },
  async beforeMount() {
    const fetch_result_structure = await this.fetch_without_data("/get/onLoad/");
    let structures_result = await fetch_result_structure.json()
    this.structure_names_original = structures_result["structures"];
    this.structure_names = Array.from(this.structure_names_original);
    this.active_structure = this.structure_names[0];
    this.multiplicity_models = structures_result["multiplicity_models"];
    this.model_names = structures_result["models"];
    this.instruments = structures_result["instruments"]
  },
  mounted() {
    // Sets the dropdowns to automatically choose for testing
    if (this.active_instrument !== "" && this.active_model !== "") {
      this.onChange();
    }
  },
  template: template,
}

