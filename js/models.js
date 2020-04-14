/*
 * Update the page when a new model is selected
 */
function selectModel(model, runSASCALC = true) {
    var modelParams = document.getElementById("modelParams");
    // Show the node
    modelParams.style.display = "inline-block";
    // Remove existing nodes
    while (modelParams.lastChild) {
        modelParams.removeChild(modelParams.lastChild);
    }
    if (window.instrument != null) {
        var instrument = window.instrument;
    }
    else {
        var instrument = document.getElementById('instrumentSelector').value;
    }
    var params = window.modelList[model]["params"];
    var paramNames = params.map(({ name }) => name);
    var defaultValues = params.map(({ value }) => value);
    var units = params.map(({ unit }) => unit);
    // Create new nodes for parameters
    for (var i = 0; i < paramNames.length; i++) {
        var id = model + "_" + paramNames[i];
        var value = (units[i] != "") ? math.unit(defaultValues[i], units[i]).toNumeric() : defaultValues[i];
        var input = createChildElementWithLabel(modelParams, 'input', { 'id': id, 'value': value }, '', paramNames[i].charAt(0).toUpperCase() + paramNames[i].slice(1) + ": ");
        input.oninput = function () {
            if (window.currentInstrument != null) {
                window.currentInstrument.SASCALC()
            } else {
                SASCALC(instrument);
            }
        }
    }
    if (runSASCALC) {
        if (window.currentInstrument != null) {
            window.currentInstrument.SASCALC()
        } else {
            SASCALC(instrument);
        }
    }
}

/*
 * Calculate the model function used to represent the data
 */
function calculateModel() {
    var model = document.getElementById("model").value;
    var paramList = window.modelList[model]["params"];
    var units = paramList.map(({ unit }) => unit);
    defaultParams = paramList.map(({ name }) => name);
    params = [];
    for (var i = 0; i < defaultParams.length; i++) {
        var paramName = model + "_" + defaultParams[i];
        var unitless = parseFloat(document.getElementById(paramName).value);
        var value = (units[i] != "" && units[i] != null) ? math.unit(unitless, units[i]) : unitless;
        params[i] = value;
    }
    // 1D calculation
    params.push(window.qValues);
    window.aveIntensity = math.dotMultiply(window.fSubs, window[model.toLowerCase()](params));
    params.pop(window.qValues);
    // 2D calculation
    var q = q_closest = qx = qy = index = 0;
    qx = window.qxValues;
    qy = window.qyValues;
    q = math.sqrt(math.add(math.multiply(qx, qx), math.multiply(qy, qy)));
    params.push(q);
    window.intensity2D = math.dotMultiply(window.fSubs, window[model.toLowerCase()](params));
    params.pop(q);
    window.intensity2D = window.intensity2D[0].map((col, i) => window.intensity2D.map(row => row[i]));
}

/*
 * Debye model for simulating intensities
 */
function debye(params) {
    // params are: [0] scale factor, [1] radius of gyration [A], [2] background [cm-1], [3] q value [A^-1]

    // calculates (scale*debye)+bkg
    var scale = params[0];
    var rg = params[1];
    var bkg = params[2];
    var q = params[3];
    // FIXME: array multiplication - work on
    var qSquared = math.dotMultiply(q, q);
    var rgSquared = math.pow(rg, 2);
    var qrSquared = math.dotMultiply(qSquared, rgSquared);
    var qrSquaredNeg = math.multiply(qrSquared, -1);
    var pOfQ = math.dotDivide(math.dotMultiply(2, math.add(math.exp(qrSquaredNeg), -1, qrSquared)), math.dotMultiply(qrSquared, qrSquared));

    //scale
    pOfQ = math.multiply(pOfQ, scale);
    // then add in the background
    return math.add(pOfQ, bkg);
}

/*
 * Sphere model for simulating intensities
 */
function sphere(params) {
    // params are: [0] scale factor, [1] radius [A], [2] deltaRho [cm-1], [3] background [cm-1], [4] q value [A^-1]

    // calculates scale * f^2 / volume where f = volume * 3 * deltaRho * (sin(qr) - q*r*cos(qr)) / (q*r)^3
    var scale = params[0];
    var radius = params[1];
    var sldSphere = math.multiply(params[2], 10e-6);
    var sldSolvent = math.multiply(params[3], 10e-6);
    var bkg = params[4];
    var q = params[5];
    var deltaRho = math.subtract(sldSphere, sldSolvent);

    var radius_cubed = math.pow(radius, 3);
    var q_rad = math.multiply(q, radius);
    var deltaRhoSquared = math.pow(deltaRho, 2);

    // FIXME: Need to do this in a linearized way
    if (q == 0) {
        return math.add(math.multiply(math.divide(4, 3), math.PI, radius_cubed, deltaRhoSquared, scale, 1e8), bkg);
    }

    var bessel = math.divide(math.multiply(3, math.subtract(math.sin(q_rad), math.multiply(q_rad, math.cos(q_rad)))), math.pow(q_rad, 3));
    var volume = math.divide(math.multiply(4, Math.PI, radius_cubed), 3);
    var f = math.multiply(volume, bessel, deltaRho);

    var f_squared = math.divide(math.multiply(f, f, 1e8), volume);

    // then add in the background
    return math.add(math.multiply(f_squared, scale), bkg);
}

// Models
window.modelList = {
    "debye": {
        "params": [
            { 'name': "scale", "value": 1000, "unit": ''},
            { 'name': "rg", "value": 100, "unit": 'angstrom' },
            { 'name': "bkg", "value": 0.0, "unit": '' },
        ],
    },
    "sphere": {
        "params": [
            { 'name': "scale", "value": 1, "unit": '' },
            { 'name': "radius", "value": 1000, "unit": 'angstrom' },
            { 'name': "sld_sphere", "value": 1.0, "unit": 'angstrom^-2' },
            { 'name': "sld_solvent", "value": 6.3, "unit": 'angstrom^-2' },
            { 'name': "bkg", "value": 0.1, "unit": '' },
        ]
    }
}