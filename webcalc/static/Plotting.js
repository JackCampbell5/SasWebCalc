import 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.17.1/plotly.min.js';
import {averagingInputs, chartColors} from "./constants.js";

const template = `
<div id="sasCalcCharts">
  <label for="offsetTraces">Offset Frozen Calculations:</label><input type="checkbox" id="offsetTraces" v-model="offsetTraces" />
  <input type="button" v-model="doFreeze" @click="freezeCalculation"/>
  <input type="button" v-if="frozen" v-model="unFrozen" @click="unfreezeCalculations"/>
  <div class="chart" id="sasCalc1DChart"></div>
  <div class="chart" id="sasCalc2DChart"></div>
</div>
`

export default {
  props: {
    offsetTraces: Boolean,
    doFreeze: String,
    unFrozen: String,
    frozen_data: Array,
    data_1d: {type: Object, default: {}},
    data_2d: {type: Object, default: {}},
  },
  watch: {
      data_1d: {
          handler(newValue, oldValue) {
            this.data_1d['qMin'] = Math.log10(Math.min(this.data_1d['qValues']));
            this.data_1d['qMax'] = Math.log10(Math.max(this.data_1d['qValues']));
            this.data_1d['iMin'] = Math.log10(Math.min(this.data_1d['intensity']));
            this.data_1d['iMax'] = Math.log10(Math.max(this.data_1d['intensity']));
            this.update1DChart();
          }
      },
      data_2d: {
          handler(newValue, oldValue) {
            this.data_2d['qxMin'] = Math.log10(Math.min(this.data_2d['qxValues']));
            this.data_2d['qxMax'] = Math.log10(Math.max(this.data_2d['qxValues']));
            this.data_2d['qyMin'] = Math.log10(Math.min(this.data_2d['qyValues']));
            this.data_2d['qyMax'] = Math.log10(Math.max(this.data_2d['qyValues']));
            this.update2DChart();
          }
      },
      frozen_data: {
          handler(newValue, oldValue) {
            this.update1DChart();
          }
      }
  },
  methods: {
    update() {
      this.update1DChart()
      this.update2DChart();
    },
    update1DChart() {
      let dataSet = {
        x: this.data_1d['qValues'],
        y: this.data_1d['intensity'],
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
            range: [this.data_1d['qMin'], this.data_1d['qMax']],
            type: 'log'
        },
        yaxis: {
            exponentformat: 'power',
            title: 'Relative Intensity (Au)',
            range: [this.data_1d['iMin'], this.data_1d['iMax']],
            type: 'log'
        },
      };
      Plotly.newPlot('sasCalc1DChart', this.frozen_data.push(dataSet), layout);

    },
    update2DChart() {
      let dataSet = {
        x: this.data_2d['qxValues'],
        y: this.data_2d['qyValues'],
        z: this.data_2d['intensity2D'],
        type: 'heatmap',
        colorscale: 'Portland'
      };
      let layout = {
        title: "SASCALC 2D Plot",
        xaxis: {
            title: "Qx (Å^-1)",
            range: [this.data_2d['qxMin'], this.data_2d['qxMax']],
            constrain: 'domain',
        },
        yaxis: {
            title: "Qy (Å^-1)",
            range: [this.data_2d['qyMin'], this.data_2d['qyMax']],
        },
        shapes: this.makeAveragingShapes(),
      };
      Plotly.newPlot('sasCalc2DChart', [dataSet], layout);
    },
    freezeCalculation() {
        let len = this.frozen_data.length;
        let offset = this.offsetTraces ? 1 + (len + 1) * 0.10 : 1;
        console.log(offset);
        let dataSet = {
            x: this.data_1d['qValues'] * offset,
            y: this.data_1d['intensity'],
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
    },
    unfreezeCalculations() {
        this.frozen_data = [];
    },
    makeAveragingShapes() {
      // TODO: convert this...
      let d3 = Plotly.d3;
      return {};
    }
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
        qMin: Math.log10(0.0001),
        qMax: Math.log10(1.0),
        iMin: Math.log10(0.001),
        iMax: Math.log10(100000),
      };
      this.data_1d['qMin'] = Math.log10(Math.min(this.data_1d['qValues']));
      this.data_1d['qMax'] = Math.log10(Math.max(this.data_1d['qValues']));
      this.data_1d['iMin'] = Math.log10(Math.min(this.data_1d['intensity']));
      this.data_1d['iMax'] = Math.log10(Math.max(this.data_1d['intensity']));
      this.data_2d = {
          qxValues: [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]],
          qyValues: [[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]],
          intensity2D: [[0, 0, 0],[0, 1130, 0],[0, 0, 0]],
          qxMin: Math.log10(0.0001),
          qxMax: Math.log10(1.0),
          qyMin: Math.log10(0.001),
          qyMax: Math.log10(100000),
      };
      this.data_2d['qxMin'] = Math.log10(Math.min(this.data_2d['qxValues']));
      this.data_2d['qxMax'] = Math.log10(Math.max(this.data_2d['qxValues']));
      this.data_2d['qyMin'] = Math.log10(Math.min(this.data_2d['qyValues']));
      this.data_2d['qyMax'] = Math.log10(Math.max(this.data_2d['qyValues']));
    this.update();
  },
  template: template,
}