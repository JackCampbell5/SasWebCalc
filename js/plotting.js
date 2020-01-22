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
        colorscale: 'Portland'
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
        },
        shapes: makeAveragingShapes(),
    };
    Plotly.newPlot('sasCalc2DChart', [dataSet], layout);
}

/*
 * Make shapes based on the averaging type and parameters on the page
 */
function makeAveragingShapes() {
    var d3 = Plotly.d3;
    var averagingType = document.getElementById('averagingType').value;

    // Get average parameters for the averaging type
    var typeParamNames = window.averagingInputs[averagingType];
    var paramVals = {};
    for (typeParam in typeParamNames) {
        var typeParamVal = typeParamNames[typeParam];
        var paramVal = document.getElementById(typeParamVal).value;
        paramVals[typeParamVal] = paramVal;
    }
    var maxQx = d3.max(window.qxValues);
    if (Number.isNaN(maxQx)) { maxQx = 1; }
    var maxQy = d3.max(window.qyValues);
    if (Number.isNaN(maxQy)) { maxQy = 1; }
    var minQx = d3.min(window.qxValues);
    if (Number.isNaN(maxQx)) { maxQx = 1; }
    var minQy = d3.min(window.qyValues);
    if (Number.isNaN(maxQy)) { maxQy = 1; }
    var ratio = Math.abs(maxQx / minQx);

    // Create the shape(s) needed for the averaging type
    var shapes = [];
    switch (averagingType) {
        default:
        case "circular":
            // No shape necessary
            break;
        case "sector":
        // FIXME: Fix this for offsets
            var detector = paramVals['detectorSections'];
            var phi = parseFloat(paramVals['phi']) * Math.PI / 180;
            var dPhi = parseFloat(paramVals['dPhi']) * Math.PI / 180;
            var phiUp = phi + dPhi;
            var phiDown = phi - dPhi;
            var phiTwoPi = Math.PI * 2 + phi;
            var phiUpTwoPi = Math.PI * 2 + phiDown;
            var phiDownTwoPi = Math.PI * 2 + phiUp;
            var phiToURCorner = Math.tan(maxQy / maxQx);
            var phiToULCorner = Math.tan(maxQy / minQx);
            var phiToLLCorner = Math.tan(minQy / minQx);
            var phiToLRCorner = Math.tan(minQy / maxQx);
            if (detector == "both" || detector == "right") {
                shapes.push(makeLine(0, 0, (phi > phiToURCorner && phi < phiToULCorner) ? maxQy / Math.tan(phi) : maxQx,
                    (phi > phiToURCorner && phi < phiToULCorner) ? maxQy : maxQx * Math.tan(phi)));
                shapes.push(makeLine(0, 0, (phiUp > phiToURCorner && phiUp < phiToULCorner) ? maxQy / Math.tan(phiUp) : maxQx,
                    (phiUp > phiToURCorner && phiUp < phiToULCorner) ? maxQy : maxQx * Math.tan(phiUp), "orange"));
                shapes.push(makeLine(0, 0, (phiDown > phiToURCorner && phiDown < phiToULCorner) ? maxQy / Math.tan(phiDown) : maxQx,
                    (phiDown > phiToURCorner && phiDown < phiToULCorner) ? maxQy : maxQx * Math.tan(phiDown), "orange"));
            }
            if (detector == "both" || detector == "left") {
                shapes.push(makeLine(0, 0, (phiTwoPi > phiToLLCorner && phiTwoPi < phiToLRCorner) ? minQy / Math.tan(phiTwoPi) : minQx,
                    (phiTwoPi > phiToLLCorner && phiTwoPi < phiToLRCorner) ? minQy : minQx * Math.tan(phiTwoPi)));
                shapes.push(makeLine(0, 0, (phiUpTwoPi > phiToLLCorner && phiUpTwoPi < phiToLRCorner) ? minQy / Math.tan(phiUpTwoPi) : minQx,
                    (phiUpTwoPi > phiToLLCorner && phiUpTwoPi < phiToLRCorner) ? minQy : minQx * Math.tan(phiUpTwoPi), "orange"));
                shapes.push(makeLine(0, 0, (phiDownTwoPi > phiToLLCorner && phiDownTwoPi < phiToLRCorner) ? minQy / Math.tan(phiDownTwoPi) : minQx,
                    (phiDownTwoPi > phiToLLCorner && phiDownTwoPi < phiToLRCorner) ? minQy : minQx * Math.tan(phiDownTwoPi), "orange"));
            }
            break;
        case "annular":
            var qCenter = parseFloat(paramVals['qCenter']);
            var qWidth = parseFloat(paramVals['qWidth']);
            var innerQ = qCenter - qWidth;
            var outerQ = qCenter + qWidth;
            shapes.push(makeCircle(-1 * qCenter, -1 * qCenter, qCenter, qCenter, "white"));
            shapes.push(makeCircle(-1 * innerQ, -1 * innerQ, innerQ, innerQ, "orange"));
            shapes.push(makeCircle(-1 * outerQ, -1 * outerQ, outerQ, outerQ, "orange"));
            break;
        case "rectangular":
        // TODO: Rewrite this for left and right sides of the detector
            var detector = paramVals['detectorSections'];
            var qWidth = parseFloat(paramVals['qWidth']);
            var qHeight = parseFloat(paramVals['qHeight']);
            if (detector == "left") {
                // FIXME: Write two lines, one on top and one on bottom
                shapes.push(makeRectangle(-1 * qWidth / 2, qHeight / 2, qWidth / 2, 0, "orange"));
            } else if (detector == "right") {
                shapes.push(makeRectangle(-1 * qWidth / 2, -1 * qHeight / 2, qWidth / 2, 0, "orange"));
            } else {
                shapes.push(makeRectangle(-1 * qWidth / 2, -1 * qHeight / 2, qWidth / 2, qHeight / 2, "orange"));
            }
            break;
        case "elliptical":
            var detector = paramVals['detectorSections'];
            var phi = parseFloat(paramVals['phi']) * Math.PI / 180;
            var aspectRatio = parseFloat(paramVals['aspectRatio']);
            var side = aspectRatio * maxQy;
            var start = 0;
            var end = 2 * Math.PI;
            var steps = 100;
            if (detector == "top") { end = Math.PI; steps = 50; }
            if (detector == "bottom") { start = Math.PI; steps = 50; }
            shapes.push(makeSVGPath(makeEllipseArc(0, 0, side, maxQy, start, end, phi, steps, false)));
            break;
    }
    return shapes;
}

/*
 * Return a dictionary that defines a line object in plot.ly
 */
function makeLine(x0, y0, x1, y1, color = "black") {
    return {
        type: 'line',
        xref: 'x',
        yref: 'y',
        x0: x0,
        y0: y0,
        x1: x1,
        y1: y1,
        line: {
            color: color,
        }
    };
}
/*
 * Return a dictionary that defines a circular-like object in plot.ly
 */
function makeCircle(x0, y0, x1, y1, color = "black") {
    return {
        type: 'circle',
        xref: 'x',
        yref: 'y',
        x0: x0,
        y0: y0,
        x1: x1,
        y1: y1,
        line: {
            color: color,
        }
    };
}
/*
 * Return a dictionary that defines a rectagular-like object in plot.ly
 */
function makeRectangle(x0, y0, x1, y1, color = "black") {
    return {
        type: 'rect',
        xref: 'x',
        yref: 'y',
        x0: x0,
        y0: y0,
        x1: x1,
        y1: y1,
        line: {
            color: color,
        }
    };
}
/*
 * Return a dictionary that defines a path-like object in plot.ly
 */
function makeSVGPath(path, color = "black") {
    return {
        type: 'path',
        path: path,
        line: {
            color: color,
        }
    };
}
/*
 * Return a path-like object that represents an oriented ellipse-like shape
 */
function makeEllipseArc(xCenter = 0, yCenter = 0, a = 1, b = 1, startAngle = 0, endAngle = 2 * Math.PI, orientationAngle = 0, N = 100, closed = false) {
    // FIXME: orientationAngle needs to work properly
    var x = [];
    var y = [];
    var t = makeArr(startAngle, endAngle, N);
    for (var i = 0; i < t.length; i++) {
        x[i] = xCenter + a * Math.cos(t[i] + orientationAngle);
        y[i] = yCenter + b * Math.sin(t[i] + orientationAngle);
    }
    var path = 'M ' + x[0] + ', ' + y[0];
    for (var k = 1; k < t.length; k++) {
        path += ' L' + x[k] + ', ' + y[k];
    }
    if (closed) {
        path += ' Z';
    }
    return path
}
function makeArr(startValue, stopValue, cardinality) {
    var arr = [];
    var step = (stopValue - startValue) / (cardinality - 1);
    for (var i = 0; i < cardinality; i++) {
        arr.push(startValue + (step * i));
    }
    return arr;
}
