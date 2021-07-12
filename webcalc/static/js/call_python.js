/*
A generic method to send data to the flask server that is then interpreted based on the route value

Arguments:
route -- A string describing where the data should go
data -- A JSON encoded value (array, JSON, string, number, etc.)

Send format -- {route: 'route', data: data}
 */
async function post_data(route, data)
{
    send_data = JSON.stringify(data);
    return await send(route, 'POST', send_data);
}

/*
A generic method to get data from the flask server when an update is needed

Arguments:
route -- A string describing where the data should come from

Return format -- A JSON encoded string "{route: route, data: data}"
 */
async function get_data(route)
{
    return await send(route, 'GET');
}

async function send(route, method, data=null)
{
    return new Promise(function (resolve, reject) {
        let xmlhttp = new XMLHttpRequest();
        xmlhttp.open(method, route);
        xmlhttp.setRequestHeader('Content-Type', 'application/json');
        xmlhttp.onload = function() {
            if (this.status >= 200 && this.status < 300) {
                resolve(xmlhttp.response);
            } else {
                reject({
                    status: this.status,
                    statusText: xmlhttp.statusText
                });
            }
        }
        xmlhttp.send(data);
    });
}
