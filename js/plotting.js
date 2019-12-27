/*
 * Update the 1D Chart with new data sets
 */
function update1DChart() {
    var data = [];
    var xmin = Math.log10(0.0001);
    var xmin_limit = Math.log10(0.0001);
    var xmax = Math.log10(1.0);
    var ymin = Math.log10(0.001);
    var ymin_limit = Math.log10(0.001);
    var ymax = Math.log10(100000);
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
    var qmin = Math.log10(Math.min(...window.qValues));
    var qmax = Math.log10(Math.max(...window.qValues));
    var imin = Math.log10(Math.min(...window.aveIntensity));
    var imax = Math.log10(Math.max(...window.aveIntensity));
    xmin = (xmin_limit < qmin && qmin < xmin) ? qmin : xmin;
    xmax = (qmax > xmax) ? qmax : xmax;
    ymin = (ymin_limit < imin && imin < ymin) ? imin : ymin;
    ymax = (imax > ymax) ? imax : ymax;
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
        qmin = Math.log10(Math.min(...frozenData[0]));
        qmax = Math.log10(Math.max(...frozenData[0]));
        imin = Math.log10(Math.min(...frozenData[1]));
        imax = Math.log10(Math.max(...frozenData[1]));
        xmin = (xmin_limit < qmin && qmin < xmin) ? qmin : xmin;
        xmax = (qmax > xmax) ? qmax : xmax;
        ymin = (ymin_limit < imin && imin < ymin) ? imin : ymin;
        ymax = (imax > ymax) ? imax : ymax;
        data.push(frozenDataSet);
    };
    var layout = {
        title: "SASCALC 1D Plot",
        xaxis: {
            exponentformat: 'power',
            title: "Q (Å^-1)",
            range: [xmin, xmax],
            type: 'log'
        },
        yaxis: {
            exponentformat: 'power',
            title: 'Relative Intensity (Au)',
            range: [ymin, ymax],
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
            range: [Math.min(window.qxValues), Math.max(window.qxValues)],
            constrain: 'domain'
        },
        yaxis: {
            title: "Qy (Å^-1)",
            range: [Math.min(window.qyValues), Math.max(window.qyValues)],
            scaleanchor: 'x'
        }
    };
    Plotly.newPlot('sasCalc2DChart', [dataSet], layout);
}
