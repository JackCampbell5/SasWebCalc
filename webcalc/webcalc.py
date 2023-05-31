# Decides what to do based on link given
import json
import sys

from typing import Optional, Union, Dict, List

import numpy as np
from flask import Flask, render_template, request

# import specific methods from python files
try:
    from python.link_to_sasmodels import get_model_list, get_params
    from python.link_to_sasmodels import calculate_model as calculate_m
    from python.instrument import calculate_instrument as calculate_i
    from python.helpers import decode_json, encode_json
except ModuleNotFoundError:
    # Runs the imports from webcalc only when auto-doc runs to remove errors
    from webcalc.python.link_to_sasmodels import get_model_list, get_params
    from webcalc.python.link_to_sasmodels import calculate_model as calculate_m
    from webcalc.python.instrument import calculate_instrument as calculate_i
    from webcalc.python.helpers import decode_json, encode_json

Number = Union[float, int]


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
    def calculate() -> str:
        """
        The primary method for calculating the neutron scattering for a particular model/instrument combination.
        Calls the instrument to get Q, dQ, and relative intensities.
        Calls the model to get real intensities for the Q range(s) calculated by the instrument.
        :return: A json-like string representation of all the data
        """
        data = decode_json(request.data)[0]
        json_like = json.loads(data)

        # Get instrument and instrument params out of the dict
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
            return encode_json({})

        # Make slicer circular if none given
        if not slicer:
            slicer = 'Circular'

        # Run the functions based on the data

        # Creates params for calculation from all the params
        calculate_params = {"instrument_params": instrument_params, "slicer": slicer, "slicer_params": slicer_params}

        # Calculate the instrument and slicer
        params = _calculate_instrument(instrument, calculate_params)
        # Get q in proper format
        q_1d = np.asarray(params.get('qValues', []))
        q_2d = np.asarray(params.get('q2DValues', []))

        # Calculate the 1D model
        model_1d = decode_json(_calculate_model(model, model_params, q_1d))
        comb_1d = np.asarray(model_1d[0]) * np.asarray(params.get('fSubs', []))
        params['fSubs'] = comb_1d.tolist()
        # Calculate the 2D model
        model_2d = decode_json(_calculate_model(model, model_params, q_2d))
        i_2d = np.asarray(params.get('intensity2D', []))
        comb_2d = np.asarray(model_2d[0]).reshape(i_2d.shape) * i_2d
        params['intensity2D'] = comb_2d.tolist()

        # Return all data
        return encode_json(params)

    @app.route('/calculate/model/<model_name>', methods=['POST'])
    def calculate_model(model_name: str) -> str:
        """Directly call the model calculation using a pre-defined API
        :return: A json-like string representation of a list of intensities.
        """
        data = decode_json(request.data)[0]
        json_like = json.loads(data)

        # Gets the model and model params out of the dict
        model_params = json_like.get('model_params', {})

        return _calculate_model(model_name, model_params, None)

    def _calculate_model(model_name: str, model_params: Dict[str: Union[Number, str]],
                         q: Optional[np.ndarray] = None) -> str:
        """Private method to directly call the model calculator
        :param model_name: The string representation of the model name used by sasmodels.
        :param model_params: A dictionary mapping the sasmodel parameter name to the parameter value.
        :param q: An n-dimensional array of Q values.
        :return: A json-like string representation of a list of intensities.
        """
        if not q:
            # If no instrument data sent, use a default Q range of 0.0001 to 1.0 A^-1
            q = np.logspace(0.0001, 1.0, 125)
        return calculate_m(model_name, [q.flatten()], model_params)

    @app.route('/calculate/instrument/<instrument_name>', methods=['POST'])
    def calculate_instrument(instrument_name: str) -> str:
        params = decode_json(request.data)
        # Calculates all the values and returns them
        return encode_json(_calculate_instrument(instrument_name, params))

    def _calculate_instrument(instrument_name: str, params: Dict[str, Union[Number, str]]) ->\
            Dict[str, Union[Number, str, List[Union[Number, str]]]]:
        """

        :param instrument_name: The string representation of the instrument name.
        :param params: A dictionary of parameters mapping the param name to the value.
        :return: A dictionary of calculated instrument values including Q (1D and 2D),
        """
        return calculate_i(instrument_name, params)

    return app


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    sas_calc = create_app()
    sas_calc.run(port=port, debug=True)


if __name__ == '__main__':
    main()
