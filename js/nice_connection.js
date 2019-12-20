﻿function sascalcToMoveValue() {
    var configs = {}
    var frozenConfigs = window.frozenConfigs;
    for (frozenConfig in frozenConfigs) {
        var scattConfig = Object.assign({}, frozenConfigs[frozenConfig]);
        var transConfig = Object.assign({}, frozenConfigs[frozenConfig]);
        transConfig["beamStopX.softPosition"] = "-15.0cm";
        scattConfig["attenuator.key"] = "0";
        configs[frozenConfig + " Scatt"] = scattConfig;
        configs[frozenConfig + " Trans"] = transConfig;
    }
    return configs;
}

function generateConfigName(config) {
    var SDD = parseFloat(config["geometry.sampleToAreaDetector"])/100;
    return SDD + "m";
}

function stringifyConfigMap(configs) {
    var sendString = "{";
    for (var configName in configs) {
        var config = configs[configName];
        sendString += "\"" + configName + "\"={";
        for (var node in config) {
            var value = config[node];
            sendString += "\"" + node + "\"=\"" + value + "\", "; 
        }
        sendString = sendString.slice(0, -2);
        sendString += "}, ";
    }
    sendString = sendString.slice(0, -2);
    sendString += "}";
    return sendString;
}