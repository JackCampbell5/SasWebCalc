# Decides what to do based on link given
import json
import sys

import numpy
import numpy as np
from flask import Flask, render_template, request

# import specific methods from python files
from python.link_to_sasmodels import get_model_list, get_params
from python.link_to_sasmodels import calculate_model as calculate_m
from python.instrument import calculate_instrument as calculate_i
from python.helpers import decode_json, encode_json


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

        # Gets ine instrument and instrument params out of the dict
        instrument = json_like.get('instrument', '')
        instrument_params = json_like.get('instrument_params', {})

        # Gets the model and model params out of the dict
        model = json_like.get('model', '')
        model_params = json_like.get('model_params', {})

        # Gets slicer and Slicer params out of dict
        slicer = json_like.get('averaging_type', '')
        slicer_params = json_like.get('averaging_params', {})

        # Returns if array is empty
        if instrument_params == {}:
            print("Returning Blank")
            return {}

        # Make slicer circular if none given
        if not slicer:
            slicer = 'Circular'

        # Run the functions based on the data

        # Creates params for calculation from all the params
        calculate_params = {"instrument_params": instrument_params, "slicer": slicer, "slicer_params": slicer_params}

        # Calculate the instrument and slicer
        instrument = calculate_instrument(instrument, calculate_params)

        # Get q in proper format
        params = decode_json(instrument)[0]
        q_1d = numpy.asarray(params.get('qValues', []))
        q_2d = numpy.asarray(params.get('q2DValues', []))

        # Calculate the 1D model
        model_1d = decode_json(calculate_model(model, model_params, q_1d))
        comb_1d = numpy.asarray(model_1d[0]) * numpy.asarray(params.get('fSubs', []))
        params['fSubs'] = comb_1d.tolist()
        # Calculate the 2D model
        model_2d = decode_json(calculate_model(model, model_params, q_2d))
        i_2d = numpy.asarray(params.get('intensity2D', []))
        comb_2d = numpy.asarray(model_2d[0]).reshape(i_2d.shape) * i_2d
        params['intensity2D'] = comb_2d.tolist()

        # Return all data
        return encode_json(params)

    @app.route('/calculate/model/<model_name>', methods=['POST'])
    def calculate_model(model_name, model_params=None, instrument_data=None):
        data = decode_json(request.data) if model_params is None else model_params
        param_names = list(data.keys())
        param_values = [v['default'] for v in data.values()]
        q = numpy.asarray(decode_json(request.data)[0]).flatten() if instrument_data is None else instrument_data
        params = {param_names[i]: param_values[i] for i in range(len(param_values))}
        return calculate_m(model_name, [q.flatten()], params)

    @app.route('/calculate/instrument/<instrument_name>', methods=['POST'])
    def calculate_instrument(instrument_name, params=None):
        if params is None:
            # Decodes the data received from javascript
            params = decode_json(request.data)
        # Calculates all the values and returns them
        return calculate_i(instrument_name, params)

    return app


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    sas_calc = create_app()
    sas_calc.run(port=port, debug=True)


if __name__ == '__main__':
    main()
