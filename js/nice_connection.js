/*
 * General NICE connection scheme using a callback function
 */
async function connectToNice(callback) {
    var router_spec = "NiceGlacier2/router:ws -p <port> -h <host>";
    var nice_connection = new NiceConnection();
    let hostname = document.getElementById("serverName").value;
    let username = "user";
    let password = "";
    let port = "9999";
    let ice_protocol_version = "1.1";
    await nice_connection.signin(router_spec.replace(/<host>/, hostname).replace(/<port>/, port), ice_protocol_version, false, username, password);
    let api = nice_connection.api;
    // Run the callback function and capture any return(s)
    var returnValue = await callback(nice, api);
    nice_connection.disconnect();
    return returnValue;
}

/*
 * Using the NICE api, send a set of configurations to the instrument
 */
async function sendConfigsToNice(nice, api) {
    var configs = sascalcToMoveValue();
    let existing_map = await api.readValue("configuration.map");
    for (config in configs) {
        if (existing_map.val.has(config)) {
            if (!confirm("configuration named " + config + " exists; Overwrite?")) {
                return false
            }
        }
    }
    await api.move(["configuration.mapPut", stringifyConfigMap(configs)], false);
}

/*
 * Using the NICE api, read the available wavelength spread values
 */
async function getWavelengthSpreads(nice, api) {
    // TODO: Get the static/hidden nodes in some way. Might need an API change
    var allDevices = await api.getAllDevices();
    return allDevices;
}

/*
 * Generates unique scattering and transmission configurations for each frozen config
 */
function sascalcToMoveValue() {
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
/*
 * Generates a unique configuration name for the configuration
 */
function generateConfigName(config) {
    var SDD = parseFloat(config["geometry.sampleToAreaDetector"]) / 100;
    configName = SDD + "m";
    window.configNames.push(SDD);
    // TODO: Check if the name already exists and update as needed
    return configName;
}
/*
 * Converts a list of config dictionaries to a string that can be accept by the NICE software
 */
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
