/*
A generic method to send data to the flask server that is then interpreted based on the route value

Arguments:
route -- A string describing where the data should go
data -- A JSON encodable value (array, JSON, string, number, etc.)

Send format -- {route: 'route', data: data}
 */
async function post_data(route, data)
{
    let xmlhttp = new XMLHttpRequest();
    xmlhttp.open('POST', '/json-handler');
    xmlhttp.setRequestHeader('Content-Type', 'application/json');
    xmlhttp.send(JSON.stringify({route: route, data: data}));
}

/*
A generic method to get data from the flask server when an update is needed

Arguments:
route -- A string describing where the data should come from

Return format -- A JSON encoded string "{route: route, data: data}"
 */
async function get_data(route)
{
    let xmlhttp = new XMLHttpRequest();
    xmlhttp.open('GET', '/json-handler');
    xmlhttp.setRequestHeader('Content-Type', 'application/json');
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            let data = this.response;
            return {route: route, data: JSON.parse(data)}
        }
    }
    xmlhttp.send();
}