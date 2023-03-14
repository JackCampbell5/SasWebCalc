# Decides what to do based on link given
import json
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

    @app.route('/get/models/', methods=['GET'])
    def get_all_models():
        return get_model_list()

    @app.route('/get/params/<model_name>', methods=['GET'])
    @app.route('/get/params/model/<model_name>', methods=['GET'])
    def get_model_params(model_name):
        return get_params(model_name)

    @app.route('/calculate/', methods=['POST'])
    def calculate():
        data = decode_json(request.data)[0]
        json_like = json.loads(data)
        instrument = json_like.get('instrument', '')
        instrument_params = json_like.get('instrument_params', {})
        model = json_like.get('model', '')
        model_params = json_like.get('model_params', {})
        slicer = json_like.get('averaging_type', '')
        slicer_params = json_like.get('averaging_params', {})
        if not slicer:
            slicer = 'Circular'
        instrument = calculate_instrument(instrument, instrument_params)
        # FIX
        # model_new = calculate_model(model, model_params)
        # TODO: Calculate instrument
        #  Calculate slicer (as part of instrument?)
        #  Calculate model
        #  Multiply values to get final 1D/2D data
        return instrument

    @app.route('/calculate/model/<model_name>', methods=['POST'])
    def calculate_model(model_name, model_params=None):
        # TODO: Refactor this to accept JSON-like dictionary of params like:
        #  {
        #   'q': [],
        #   'qx': [[]],
        #   'qy': [[]],
        #   'param_1': {'units': '', val: '', min: '', max: '', ...}
        #   ...
        #   'param_n': {}
        #  }
        if model_params is not None:
            data = decode_json(request.data)
        print(data)
        param_names = data[0][0]
        param_values = data[0][1]
        if len(data[0]) > 3:
            q = [np.array([np.tile(x, len(data[0][3])) for x in data[0][2]]).flatten(),
                 np.array(np.tile(data[0][3], (1, len(data[0][2])))).flatten()]
        else:
            q = [np.array(data[0][2])]
        params = {param_names[i]: param_values[i] for i in range(len(param_values))}
        return calculate_m(model_name, q, params)

    @app.route('/calculate/instrument/<instrument_name>', methods=['POST'])
    def calculate_instrument(instrument_name, params=None):
        if params is None:
            # Decodes the data received from javascript
            params = decode_json(request.data)
        # Calculates all the values and returns them
        return calculate_i(instrument_name, params)

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    sas_calc = create_app()
    sas_calc.run(port=port, debug=True)
