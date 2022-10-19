# Decides what to do based on link given
import sys

import numpy as np
from flask import Flask, render_template, request

# import specific methods from python files
from python.link_to_sasmodels import get_model_list, get_params
from python.link_to_sasmodels import calculate_model as calculate_m
from python.instrument import calculate_instrument as calculate_i
from python.helpers import decode_json


def create_app():
    app = Flask(__name__)

    # Launches the main program based on a basic link
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/saswebcalc/', methods=['GET', 'POST'])
    def root():
        return render_template("index.html")

    @app.route('/getmodels/', methods=['GET'])
    def get_all_models():
        return get_model_list()

    @app.route('/calculatemodel/<model_name>', methods=['POST'])
    def calculate_model(model_name):
        data = decode_json(request.data)
        param_names = data[0][0]
        param_values = data[0][1]
        if len(data[0]) > 3:
            q = [np.array([np.tile(x, len(data[0][3])) for x in data[0][2]]).flatten(),
                 np.array(np.tile(data[0][3], (1, len(data[0][2])))).flatten()]
        else:
            q = [np.array(data[0][2])]
        params = {param_names[i]: param_values[i] for i in range(len(param_values))}
        return calculate_m(model_name, q, params)

    @app.route('/calculate_instrument/<instrument_name>', methods=['POST'])
    def calculate_instrument(instrument_name):
        # Decodes the data received from javascript
        data = decode_json(request.data)
        # Turn from tuple into dictionary for accessing
        params = data[0];
        # Calculates all the values and returns them
        return calculate_i(instrument_name, params)

    @app.route('/getparams/<model_name>', methods=['GET'])
    def get_model_params(model_name):
        return get_params(model_name)

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    sas_calc = create_app()
    sas_calc.run(port=port, debug=True)
