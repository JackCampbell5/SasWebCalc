/*
 * Update the 1D Chart with new data sets
 */
function update1DChart() {
    var dataSet = {
        x: window.qValues,
        y: window.aveIntensity,
        mode: 'lines+markers',
        marker: {
            color: window.chartColors.black,
            size: 5,
        },
        line: {
            color: window.chartColors.black,
            size: 1,
        },
        name: "SASCALC"
    };
    var layout = {
        title: "SASCALC 1D Plot",
        xaxis: {
            title: "Q (Å^-1)",
        },
        yaxis: {
            title: 'Relative Intensity (Au)',
        }
    };
    Plotly.newPlot('sasCalc1DChart', [dataSet], layout);
}

/*
 * Update the 2D Chart with the current calculated 2D pattern
 */
function update2DChart() {
    var dataSet = {
        x: window.qxValues,
        y: window.qyValues,
        z: window.intensity2D,
        type: 'heatmap',
    };
    var layout = {
        title: "SASCALC 2D Plot",
        xaxis: {
            title: "Qx (Å^-1)",
            range: [Math.min(window.qxValues), Math.max(window.qxValues)]
        },
        yaxis: {
            title: "Qy (Å^-1)",
            range: [Math.min(window.qyValues), Math.max(window.qyValues)]
        }
    };
    Plotly.newPlot('sasCalc2DChart', [dataSet], layout);
}
