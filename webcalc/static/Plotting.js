import 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.0/plotly.min.js';
import {chartColors} from "./constants.js";

const template = `
<div class="freezer">
  <label for="offsetTraces">Offset Frozen Calculations:</label><input type="checkbox" id="offsetTraces" v-model="offsetTraces" />
  <input type="button" v-model="doFreeze" @click="freezeCalculation" />
  <input type="button" v-if="frozen" v-model="unFrozen" @click="unfreezeCalculations" />
</div>
<div id="results">
  <div class="calculatingText" v-show="calculating">
    <p id="calculating"></p>
  </div>
  <div class="plots" v-show="!calculating">
    <div id="sasCalc1DChart"></div>
    <div id="sasCalc2DChart"></div> 
  </div>
  <div class="plots" v-show="log">
    <div id="status"></div>
  </div>
</div>
`

export default {
  props: {
    data_1d: Object,
    data_2d: Object,
    shapes: Array,
    calculating_shown: Boolean,
    log_shown: Boolean,
  },
  watch: {
      data_1d: {
          handler(newValue, oldValue) {
            this.update1DChart();
          }
      },
      data_2d: {
          handler(newValue, oldValue) {
            this.update2DChart();
          }
      },
      shapes: {
          handler(newValue, oldValue) {
              if (Object.keys(this.data_2d).length > 0) {
                  this.update2DChart();
              }
          }
      },
      offsetTraces: {
          handler(newValue, oldValue) {
            this.scaleFrozenDataSets();
          }
      },
      calculating_shown: {
          handler(newValue, oldValue) {
            this.calculating = newValue;
          }
      },
      log_shown: {
          handler(newValue, oldValue) {
            this.log = newValue;
          }
      },
  },
  methods: {
    get1DCharts() {
      let dataSets= [];
      for (const [key, value] of Object.entries(this.data_1d))
      {
          let dataSet = {
            x: this.data_1d[key].qValues,
            y: this.data_1d[key].intensity,
            mode: 'lines+markers',
            marker: {
                color: chartColors.black,
                size: 5,
            },
            line: {
                color: chartColors.black,
                size: 1,
            },
            name: 'name' in value ? value.name : "SASCALC"
          };
          dataSets.push(dataSet);
      }
      return dataSets;
    },
    get2DCharts() {
      let dataSets= [];
      for (const [key, value] of Object.entries(this.data_2d))
      {
          let dataSet = {
            x: this.data_2d[key].qxValues,
            y: this.data_2d[key].qyValues,
            z: this.data_2d[key].intensity2D,
            type: 'heatmap',
            colorscale: 'Portland',
            name: 'name' in value ? value.name : "SASCALC"
          };
          dataSets.push(dataSet);
      }
      return dataSets;
    },
    update1DChart() {
      let dataSets = this.get1DCharts();
      let layout = {
        title: "SASCALC 1D Plot",
        xaxis: {
            exponentformat: 'power',
            title: "Q (Å^-1)",
            type: 'log'
        },
        yaxis: {
            exponentformat: 'power',
            title: 'Relative Intensity (Au)',
            type: 'log'
        },
      };
      dataSets.push.apply(dataSets, this.frozen_data);
      Plotly.newPlot('sasCalc1DChart', dataSets, layout);
      this.persist()
    },
    update2DChart() {
      let dataSets = this.get2DCharts();
      let layout = {
        title: "SASCALC 2D Plot",
        xaxis: {
            title: "Qx (Å^-1)",
            constrain: 'domain',
        },
        yaxis: {
            title: "Qy (Å^-1)",
            scaleanchor: "x",
            scaleratio: 1,
        },
        shapes: this.shapes,
      };
      Plotly.newPlot('sasCalc2DChart', dataSets, layout);
      this.persist()
    },
    freezeCalculation() {
      let dataSets = this.get1DCharts();
      for (const [key, frozen] in Object.entries(dataSets)) {
          dataSets[key].raw = dataSets[key].y;
          dataSets[key].mode = 'lines+markers';
          this.frozen_data.push(dataSets[key]);
      }
      this.scaleFrozenDataSets();
    },
    unfreezeCalculations() {
        this.frozen_data = [];
        this.update1DChart();
        this.persist();
    },
    scaleFrozenDataSets() {
        let scale = 1.0;
        let offset = this.offsetTraces ? 1 : 0;
        for (let x in this.frozen_data) {
            this.frozen_data[x].name = 'frozen_' + x;
            this.frozen_data[x].marker = {
                color: chartColors[this.frozen_data.length],
                size: 1,
            };
            this.frozen_data[x].line = {
                color: chartColors[this.frozen_data.length],
                size: 1,
            };
            scale = scale * Math.exp(offset);
            this.frozen_data[x].y = this.frozen_data[x].raw.map(element => element * scale);
        }
        this.update1DChart();
        this.persist();
      },
    getMax(array) {
        return Math.max(...array.map(e => Array.isArray(e) ? this.getMax(e) : e))
    },
    getMin(array) {
        return Math.min(...array.map(e => Array.isArray(e) ? this.getMin(e) : e))
    },
    persist() {
      /*
      Store the current values into active memory to be recalled if the page is refreshed.
       */
        localStorage.setItem("offsetTraces", String(this.offsetTraces));
        localStorage.setItem("frozen_data", JSON.stringify(this.frozen_data));
    },
    loadPersistentState() {
        this.offsetTraces = localStorage.getItem("offsetTraces") === "true";
        this.frozen_data = JSON.parse(localStorage.getItem("frozen_data")) || [];
    }
  },
  data: () => ({
    offsetTraces: false,
    frozen_data: [],
    doFreeze: "Freeze Calculation",
    unFrozen: "Unfreeze Calculations",
    calculating: false,
    log: false,
  }),
  computed: {
    frozen() {
      return this.frozen_data !== [];
    }
  },
  mounted() {
    this.loadPersistentState()
  },
  template: template,
}