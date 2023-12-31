import 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.17.1/plotly.min.js';
import {chartColors} from "./constants.js";

const template = `
<div class="freezer">
  <label for="offsetTraces">Offset Frozen Calculations:</label><input type="checkbox" id="offsetTraces" v-model="offsetTraces" />
  <input type="button" v-model="doFreeze" @click="freezeCalculation" />
  <input type="button" v-if="frozen" v-model="unFrozen" @click="unfreezeCalculations" />
</div>
<div id="results">
  <div id="status">
      <div class="calculatingText" v-show="calculating">
        <p id="calculating">Calculating</p>
      </div>
  </div>
  <div id="sasCalc1DChart"></div>
  <div id="sasCalc2DChart"></div>
</div>
`

export default {
  props: {
    data_1d: Object,
    data_2d: Object,
    shapes: Array,
    calculating_shown: Boolean,
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
  },
  methods: {
    update1DChart() {
      let dataSet = {
        x: this.data_1d.qValues,
        y: this.data_1d.intensity,
        mode: 'lines+markers',
        marker: {
            color: chartColors.black,
            size: 5,
        },
        line: {
            color: chartColors.black,
            size: 1,
        },
        name: "SASCALC"
      };
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
      let dataSets = [];
      dataSets.push(dataSet)
        dataSets.push.apply(dataSets, this.frozen_data);
      Plotly.newPlot('sasCalc1DChart', dataSets, layout);
    },
    update2DChart() {
      let dataSet = {
        x: this.data_2d.qxValues,
        y: this.data_2d.qyValues,
        z: this.data_2d.intensity2D,
        type: 'heatmap',
        colorscale: 'Portland'
      };
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
      Plotly.newPlot('sasCalc2DChart', [dataSet], layout);
    },
    freezeCalculation() {
        let dataSet = {
            x: this.data_1d.qValues,
            y: this.data_1d.intensity,
            raw: this.data_1d.qValues,
            mode: 'lines+markers',
            marker: {
                color: chartColors[this.frozen_data.length],
                size: 5,
            },
            line: {
                color: chartColors[this.frozen_data.length],
                size: 1,
            },
            name: "frozen" + this.frozen_data.length,
          };
        this.frozen_data.push(dataSet);
        this.scaleFrozenDataSets();
    },
    unfreezeCalculations() {
        this.frozen_data = [];
        this.update1DChart();
    },
    scaleFrozenDataSets() {
        let scale = 1.0;
        let offset = this.offsetTraces ? 1.0 : 0.0;
        for (let x in this.frozen_data) {
            scale = scale + offset;
            this.frozen_data[x].x = this.frozen_data[x].raw.map(function(element) {return element * scale;})
        }
        this.update1DChart();
      },
    getMax(array) {
        return Math.max(...array.map(e => Array.isArray(e) ? this.getMax(e) : e))
    },
    getMin(array) {
        return Math.min(...array.map(e => Array.isArray(e) ? this.getMin(e) : e))
    }
  },
  data: () => ({
    offsetTraces: false,
    frozen_data: [],
    doFreeze: "Freeze Calculation",
    unFrozen: "Unfreeze Calculations",
    calculating: false,
  }),
  computed: {
    frozen() {
      return this.frozen_data !== [];
    }
  },
  template: template,
}