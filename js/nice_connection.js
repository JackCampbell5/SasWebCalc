function sendToNICE() {
    var router_spec = "NiceGlacier2/router:ws -p <port> -h <host>";
    var nice_connection = new NiceConnection();
    let hostname = document.getElementById("nice_hostname").value;
    let username = "user";
    let password = "";
    let port = "9999";
    let ice_protocol_version = "1.1";
    await nice_connection.signin(router_spec.replace(/<host>/, hostname).replace(/<port>/, port), ice_protocol_version, false, username, password);
    let api = nice_connection.api;
    let existing_map = await api.readValue("configuration.map");
    if (existing_map.val.has(app.name)) {
        if (!confirm("configuration named " + app.name + " exists; Overwrite?")) {
            return false
        }
    }
    api.move(["configuration.mapPut", sascalcToMoveValue(app)], false)
    nice_connection.disconnect();
}

function sascalcToMoveValue() {
    var currentConfig = window.currentConfigs;
    var frozenConfigs = window.frozenConfigs;
}