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
    var instrument = document.getElementById('instrumentSelector').value;
    populateModelParams(model);
    if (runSASCALC) {
        SASCALC(instrument);
    }
}

/*
 * Get a list of models directly from sasmodels
 */
async function populateModelSelector(modelInput) {
    let route = '/getmodels/';
    let rawData = await get_data(route);
    modelInput.innerHTML = '';
    let myArr = JSON.parse(rawData);
    for (let index in myArr) {
        var modelname = myArr[index];
        let nextChild = document.createElement('option', {'value': modelname});
        nextChild.innerHTML = modelname;
        modelInput.appendChild(nextChild);
    }
}

/*
 * Get model params from model name
 */
async function populateModelParams(modelName) {
    let route = '/getparams/' + modelName;
    let rawData = await get_data(route);
    let param_dict = JSON.parse(rawData)
    var modelParams = document.getElementById("modelParams");
    // Show the node
    modelParams.style.display = "inline-block";
    // Remove existing nodes
    while (modelParams.lastChild) {
        modelParams.removeChild(modelParams.lastChild);
    }
    var paramNames = Object.keys(param_dict);
    var paramValues = Object.values(param_dict);
    // Create new nodes for parameters
    var ul = document.createElement("ul");
    for (var i = 0; i < paramNames.length; i++) {
        var li = document.createElement("li");
        var id = modelName + "_" + paramNames[i];
        var label = document.createElement("LABEL");
        var for_att = document.createAttribute("for");
        for_att.value = id;
        label.setAttributeNode(for_att);
        var labelValue = "  " + paramNames[i].charAt(0).toUpperCase() + paramNames[i].slice(1);
        if (paramValues[i]['units'] !== "") {
            labelValue = labelValue + " (" + paramValues[i]['units'] + ")";
        }
        labelValue = labelValue + ": ";
        label.innerHTML = labelValue;
        var input = document.createElement("input");
        var id_att = document.createAttribute("id");
        id_att.value = id;
        input.setAttributeNode(id_att);
        var type_att = document.createAttribute("type");
        type_att.value = 'number';
        input.setAttributeNode(type_att);
        if (paramValues[i]['lower_limit'] !== '-inf') {
            var low_lim = document.createAttribute("min");
            low_lim.value = paramValues[i]['lower_limit'];
            input.setAttributeNode(low_lim);
        }
        if (paramValues[i]['upper_limit'] !== 'inf') {
            var up_lim = document.createAttribute("max");
            up_lim.value = paramValues[i]['upper_limit'];
            input.setAttributeNode(up_lim);
        }
        input.value = paramValues[i]['default'];
        li.appendChild(label);
        li.appendChild(input);
        ul.appendChild(li);
    }
    modelParams.appendChild(ul);
}

/*
 * Calculate the model function used to represent the data
 */
async function calculateModel() {
    var model = document.getElementById("model").value;
    let params_route = '/getparams/' + model;
    let calc_route = '/calculatemodel/' + model;
    let rawData = await get_data(params_route);
    let params = JSON.parse(rawData);
    var paramNames = Object.keys(params);
    var paramValues = [];
    for (var i = 0; i < paramNames.length; i++) {
        var paramName = model + "_" + paramNames[i];
        paramValues[i] = parseFloat(document.getElementById(paramName).value);
    }
    // 1D calculation
    var data1D = [];
    data1D[0] = paramNames;
    data1D[1] = paramValues;
    data1D[2] = window.qValues;
    var modelCalc1D = await post_data(calc_route, data1D);
    console.log(modelCalc1D);
    window.aveIntensity = JSON.parse(modelCalc1D);
    // 2D calculation
    var data2D = [];
    data2D[0] = paramNames;
    data2D[1] = paramValues;
    data2D[2] = window.qxValues;
    data2D[3] = window.qyValues;
    var modelCalc2D = await post_data(calc_route, data2D);
    console.log(modelCalc2D);
    window.intensity2D = JSON.parse(modelCalc2D);
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
    var qrSquared = (q * rg) * (q * rg);
    var pOfQ = 2 * (Math.exp(-1 * qrSquared) - 1 + qrSquared) / Math.pow(qrSquared, 2);

    //scale
    pOfQ *= scale;
    // then add in the background
    return (pOfQ + bkg);
}

/*
 * Sphere model for simulating intensities
 */
function sphere(params) {
    // params are: [0] scale factor, [1] radius [A], [2] deltaRho [cm-1], [3] background [cm-1], [4] q value [A^-1]

    // calculates scale * f^2 / volume where f = volume * 3 * deltaRho * (sin(qr) - q*r*cos(qr)) / (q*r)^3
    var scale = params[0];
    var radius = params[1];
    var sldSphere = params[2] * 10e-6;
    var sldSolvent = params[3] * 10e-6;
    var bkg = params[4];
    var q = params[5];
    var deltaRho = sldSphere - sldSolvent;

    var radius_cubed = radius * radius * radius;
    var q_rad = q * radius;
    var deltaRhoSquared = deltaRho * deltaRho;

    if (q == 0) {
        return (4 / 3) * Math.PI * radius_cubed * deltaRhoSquared * scale * 1e8 + bkg;
    }

    var bessel = 3 * (Math.sin(q_rad) - q_rad * Math.cos(q_rad)) / (q_rad * q_rad * q_rad);
    var volume = 4 * Math.PI * radius_cubed / 3;
    var f = volume * bessel * deltaRho;

    var f_squared = (f * f / volume) * 1e8;

    // then add in the background
    return (f_squared * scale + bkg);
}
