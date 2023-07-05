import AveragingParams from './AveragingParams.js';
import {default as NG7SANS} from "./instruments/NG7SANS.js";
import {default as NGB30SANS} from "./instruments/NGB30SANS.js";
import {default as vsans} from "./instruments/VSANS.js";
import {default as NoInstrument} from "./instruments/UserDefinedQRange.js";
import {default as NGB10SANS} from "./instruments/NGB10SANS.js";
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
      <select id="instrumentSelector" v-model="active_instrument">
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
  <div class="calculatingText" v-show="calculating_shown">
    <p id="calculating">Calculating</p>
  </div> 
  <div class="documentation" v-show="documentation_shown">
  <iframe src="/docs/index.html" title="SasWebCalc Documentation"  width="100%" height="500" style="border:1px solid black;"></iframe>
  </div>
  <plotting ref="plotting" :data_1d="data_1d" :data_2d="data_2d" :shapes="shapes"/>
 
  <div class="instrument-section" id="modelAndAveragingParams">
    <averaging-params ref="averaging_params" :active_averaging_type="active_averaging_type" :data_1d="data_1d"
        :data_2d="data_2d" @change-shapes="onShapeChange" @change-ave-params="onAveragingChange"/>
    <model-params ref="model" :active_model="active_model" :model_names="model_names" :model_params="model_params"
        @model-value-change="onModelParamChange" />
  </div>
  <div class="instrument-section" id="instrumentParams">
    <component v-if="active_instrument != ''" :is="active_instrument" :title="instruments[active_instrument]" :pythonParams="pythonParams"
        @value-change="onInstrumentParamChange"/>
  </div>
</div>
</main>
`;

export default {
  components: {
    'averaging-params': AveragingParams,
    'model-params': model,
    'plotting': plotting,
    'NoInstrument': NoInstrument,
    "NGB30SANS": NGB30SANS,
    "NG7SANS": NG7SANS,
    "NGB10SANS": NGB10SANS,
    "vsans": vsans
  },
  data: () => ({
    active_instrument: "",
    active_averaging_type: "Circular",
    available_instruments: ["NG7SANS","NGB10SANS","NGB30SANS","NoInstrument"],
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
    pythonParams: {},
    documentation_shown: false,
    calculating_shown: false,
  }),
  methods: {
    async populateModelParams() {
      if(this.active_model !== ""){
        let model_name = this.active_structure !== this.structure_names[0] ? this.active_model+'@'+this.active_structure :  this.active_model
        const fetch_result = await fetch(`/get/params/model/${model_name}`);
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
          this.pythonParams = results["user_inaccessible"];
        }
        this.data_1d = {qValues:results["qValues"],intensity:results["fSubs"]};
        this.data_2d = {qxValues:results["qxValues"],qyValues:results["qyValues"],intensity2D: results["intensity2D"]};
        this.calculating_shown = false;

      }//End if statement to check instrument existence

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
    const fetch_result_structure = await fetch("/get/onLoad/");
    let structures_result = await fetch_result_structure.json()
    this.structure_names_original = structures_result["structures"];
    this.structure_names = Array.from(this.structure_names_original);
    this.active_structure = this.structure_names[0];
    this.multiplicity_models = structures_result["multiplicity_models"];
    this.model_names = structures_result["models"];
    let instrument_options = structures_result["instruments"]
    for (let a in instrument_options){
      if(this.available_instruments.includes(a)){
        this.instruments[a] = instrument_options[a]
      }
    }
  },
  mounted() {
    // Sets the dropdowns to automatically choose for testing
    if (this.active_instrument !== "" && this.active_model !== "") {
      this.onChange();
    }
  },
  template: template,
}

