/*
 * Update the 1D Chart with new data sets
 */
function update1DChart() {
    var data = [];
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
    data.push(dataSet);
    for (frozen in window.frozenCalculations) {
        var frozenData = window.frozenCalculations[frozen];
        var color = window.chartColors[frozen];
        var title = `Frozen ${frozen}`;
        var frozenDataSet = {
            x: frozenData[0],
            y: frozenData[1],
            mode: 'lines+markers',
            marker: {
                color: color,
                size: 5,
            },
            line: {
                color: color,
                size: 1,
            },
            name: title
        };
        data.push(frozenDataSet);
    };
    var layout = {
        title: "SASCALC 1D Plot",
        xaxis: {
            exponentformat: 'power',
            title: "Q (Å^-1)",
            type: 'log'
        },
        yaxis: {
            exponentformat: 'power',
            title: 'Relative Intensity (Au)',
            range: [1e-5, NaN],
            type: 'log'
        }
    };
    Plotly.newPlot('sasCalc1DChart', data, layout);
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
