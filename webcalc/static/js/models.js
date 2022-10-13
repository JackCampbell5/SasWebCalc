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
    window.modelList[modelName] = {'params': {}}
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
        window.modelList[modelName]['params'][paramNames[i]] = paramValues[i];
        window.modelList[modelName]['params'][paramNames[i]]['currentValue'] = paramValues[i]['default'];
    }
    modelParams.appendChild(ul);
}

/*
 * Calculate the model function used to represent the data
 */
async function calculateModel() {
    //TODO FIX:  Function not running fully on page load
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
    window.aveIntensity = parseJSON(modelCalc1D);
    // 2D calculation
    var data2D = [];
    data2D[0] = paramNames;
    data2D[1] = paramValues;
    data2D[2] = window.qxValues;
    data2D[3] = window.qyValues;
    var modelCalc2D = await post_data(calc_route, data2D);
    window.intensity2D = redimension2D(parseJSON(modelCalc2D));
}

function parseJSON(jsonString) {
    var inf = 9999999;
    var negInf = -9999999;
    var nan = 8888888;
    var newArray = JSON.parse(jsonString);
    // Replace all input values with real values
    while (newArray.indexOf(inf) >= 0) {
        newArray[newArray.indexOf(inf)] = Infinity;
    } while (newArray.indexOf(negInf) >= 0) {
        newArray[newArray.indexOf(negInf)] = -1*Infinity;
    } while (newArray.indexOf(nan) >= 0) {
        newArray[newArray.indexOf(nan)] = NaN;
    }
    return newArray;
}

function redimension2D(array) {
    var finalArray = [];
    while(array.length > 0) {
        finalArray.push(array.splice(0, window.qxValues.length));
    }
    return finalArray
}