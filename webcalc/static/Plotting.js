import 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.17.1/plotly.min.js';
import {chartColors} from "./constants.js";
import {default as AveragingParams} from "./AveragingParams.js";

const template = `
<div class="freezer">
  <label for="offsetTraces">Offset Frozen Calculations:</label><input type="checkbox" id="offsetTraces" v-model="offsetTraces" />
  <input type="button" v-model="doFreeze" @click="freezeCalculation"/>
  <input type="button" v-if="frozen" v-model="unFrozen" @click="unfreezeCalculations"/>
</div>
<div id="sasCalcCharts">
  <div id="sasCalc1DChart"></div>
  <div id="sasCalc2DChart"></div>
</div>
`

export default {
  watch: {
      data_1d: {
          handler(newValue, oldValue) {
            this.data_1d.qMin = Math.log10(Math.min(...this.data_1d.qValues));
            this.data_1d.qMax = Math.log10(Math.max(...this.data_1d.qValues));
            this.data_1d.iMin = Math.log10(Math.min(...this.data_1d.intensity));
            this.data_1d.iMax = Math.log10(Math.max(...this.data_1d.intensity));
            this.update1DChart();
          }
      },
      data_2d: {
          handler(newValue, oldValue) {
            this.data_2d.qxMin = Math.log10(Math.min(...this.data_2d.qxValues));
            this.data_2d.qxMax = Math.log10(Math.max(...this.data_2d.qxValues));
            this.data_2d.qyMin = Math.log10(Math.min(...this.data_2d.qyValues));
            this.data_2d.qyMax = Math.log10(Math.max(...this.data_2d.qyValues));
            this.update2DChart();
          }
      },
      offsetTraces: {
          handler(newValue, oldValue) {
            this.scaleFrozenDataSets();
          }
      }
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
            range: [this.data_1d.qMin, this.data_1d.qMax],
            type: 'log'
        },
        yaxis: {
            exponentformat: 'power',
            title: 'Relative Intensity (Au)',
            range: [this.data_1d.iMin, this.data_1d.iMax],
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
            range: [this.data_2d.qxMin, this.data_2d.qxMax],
            constrain: 'domain',
        },
        yaxis: {
            title: "Qy (Å^-1)",
            range: [this.data_2d.qyMin, this.data_2d.qyMax],
        },
        shapes: AveragingParams.shapes,
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
  },
  data: () => ({
    offsetTraces: false,
    frozen_data: [],
    data_1d: {},
    data_2d: {},
    doFreeze: "Freeze Calculation",
    unFrozen: "Unfreeze Calculations",
  }),
  computed: {
    frozen() {
      return this.frozen_data !== [];
    }
  },
  mounted() {
      this.data_1d = {
        qValues: [0.0001, 0.001, 0.01, 0.1],
        intensity: [1000, 100, 10, 1],
        qMin: 0.0001,
        qMax: 1.0,
        iMin: 0.001,
        iMax: 100000,
      };
      this.data_2d = {
          qxValues: [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]],
          qyValues: [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]],
          intensity2D: [[0, 0, 0],[0, 1130, 0],[0, 0, 0]],
          qxMin: 0.0001,
          qxMax: 1.0,
          qyMin: 0.001,
          qyMax: 100000,
      };
  },
  template: template,
}