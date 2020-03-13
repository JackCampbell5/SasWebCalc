/*
 * General NICE connection scheme using a callback function
 */
async function connectToNice(callback = null, server="", persistConnection = false) {
    var router_spec = "NiceGlacier2/router:ws -p <port> -h <host>";
    try {
        var nice_connection = new NiceConnection();
    } catch (error) {
        console.error(error);
        return null;
    }
    if (server == "") {
        var hostname = document.getElementById("serverName").value;
    } else {
        var hostname = server;
    }
    let username = "user";
    let password = "";
    let port = "9999";
    let ice_protocol_version = "1.1";
    await nice_connection.signin(router_spec.replace(/<host>/, hostname).replace(/<port>/, port), ice_protocol_version, false, username, password);
    // Run the callback function and capture any return(s)
    if (callback != null) {
        var returnValue = await callback(nice_connection);
    }
    if (!persistConnection) {
        nice_connection.disconnect();
    }
    return returnValue;
}

/*
 * Using the NICE api, send a set of configurations to the instrument
 */
async function sendConfigsToNice(nice) {
    var configs = sascalcToMoveValue();
    let existing_map = await nice.api.readValue("configuration.map");
    for (config in configs) {
        if (existing_map.val.has(config)) {
            if (!confirm("configuration named " + config + " exists; Overwrite?")) {
                return false
            }
        }
    }
    await nice.api.move(["configuration.mapPut", stringifyConfigMap(configs)], false);
}

/*
 * Using the NICE api, read the available static nodes
 */
async function getStaticNodeMap(nice) {
    var devicesMonitor = new DevicesMonitorI();
    await Promise.all([
        nice.subscribe(devicesMonitor, 'devices'),
        devicesMonitor.subscribed,
    ]);
    return devicesMonitor.staticNodeMap;
}

/*
 * Using the NICE api, read the available devices present on the system
 */
async function getDevicesMap(nice) {
    var devicesMonitor = new DevicesMonitorI();
    await Promise.all([
        nice.subscribe(devicesMonitor, 'devices'),
        devicesMonitor.subscribed,
    ]);
    return devicesMonitor.devices;
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

/*
 * Class for monitoring devices on NICE
 * Source: http://nicedata.ncnr.nist.gov/niceweb/nicejs/devicetree_vue.html
 */
var DevicesMonitorI = class extends nice.api.devices.DevicesMonitor {
    constructor() {
        super();
        this.promise = Promise.resolve();
        var _resolve, _reject;
        this.subscribed = new Promise(function (resolve, reject) {
            _resolve = resolve;
            _reject = reject;
        })
        this.postSubscribeHooks = [function () { _resolve() }];
        this.postAddedHooks = [];
        this.postRemovedHooks = [];
        //WorkerQueue.createQueue('dataRecord', this._queueProcessor.handle_record);
    }
    onSubscribe(devices, nodes, staticNodeMap, groups, __current) {
        var devices = this.MapToObject(devices);
        var nodes = this.MapToObject(nodes);
        var groups = this.MapToObject(groups);
        var staticNodeMap = this.MapToObject(staticNodeMap);
        this.devices = devices;
        this.nodes = nodes;
        this.groups = groups;
        this.staticNodeMap = staticNodeMap;
        this.dynamic_devices = {};
        this.postChangedHooks = (this.postChangedHooks == null) ? [] : this.postChangedHooks;
        if (this.postSubscribeHooks) {
            this.postSubscribeHooks.forEach(function (callback) { callback(devices, nodes, staticNodeMap, groups); });
        }
    }
    changed(nodes, __current) {
        var changed = this.MapToObject(nodes);
        jQuery.extend(this.nodes, changed);
        this._lastChanged = changed;
        if (this.postChangedHooks) {
            this.postChangedHooks.forEach(function (callback) { callback(changed); });
        }
    }
    removed(devices, nodes, __current) {
        var devices = this.MapToObject(devices);
        var nodes = this.MapToObject(nodes);
        this._lastDevicesRemoved = devices;
        this._lastNodesRemoved = nodes;
        for (var d in devices) {
            delete this.devices[d];
        }
        for (var n in nodes) {
            delete this.nodes[n];
        }
        if (this.postRemovedHooks) {
            this.postRemovedHooks.forEach(function (callback) { callback(devices, nodes); });
        }
    }
    added(devices, nodes, staticNodeMap, __current) {
        var devices = this.MapToObject(devices);
        var nodes = this.MapToObject(nodes);
        jQuery.extend(true, this.devices, devices);
        jQuery.extend(true, this.nodes, nodes);
        //jQuery.extend(true, this.staticNodeMap, this.MapToObject(staticNodeMap));
        this._lastDevicesAdded = devices;
        this._lastNodesAdded = nodes;
        if (this.postAddedHooks) {
            this.postAddedHooks.forEach(function (callback) { callback(devices, nodes); });
        }
    }
    dynamicDevicesAdded(addRemoveID, childDeviceIDs, __current) {
        this.groups[addRemoveID] = childDeviceIDs;
    }
    dynamicDevicesRemoved(addRemoveID, __current) {
        console.log(addRemoveID);
        delete this.dynamic_devices[addRemoveID];
        delete this.groups[addRemoveID];
    }
    getAllDeviceNames() {
        var devices = [];
        this.devices.forEach(function (d) { devices.push(d); });
        return devices;
    }
    MapToObject(m) {
        var obj = {};
        m.forEach(function (value, key, map) {
            obj[key] = value;
        });
        return obj
    }
}
