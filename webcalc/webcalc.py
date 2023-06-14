# Decides what to do based on link given
import json
import sys

from typing import Optional, Union, Dict, List

import numpy as np
from flask import Flask, render_template, request

# import specific methods from python files
try:
    from python.link_to_sasmodels import get_model_list, get_params, get_model
    from python.link_to_sasmodels import calculate_model as calculate_m
    from python.instrument import calculate_instrument as calculate_i
    from python.helpers import decode_json, encode_json
    from python.instrument import get_instrument_by_name
    from python.slicers import SLICER_MAP, Circular
    from python.calculator import Calculator
except ModuleNotFoundError:
    # Runs the imports from webcalc only when auto-doc runs to remove errors
    from webcalc.python.link_to_sasmodels import get_model_list, get_params, get_model
    from webcalc.python.link_to_sasmodels import calculate_model as calculate_m
    from webcalc.python.instrument import calculate_instrument as calculate_i
    from webcalc.python.helpers import decode_json, encode_json
    from webcalc.python.instrument import get_instrument_by_name
    from webcalc.python.slicers import SLICER_MAP, Circular
    from webcalc.python.calculator import Calculator

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
        instrument_name = json_like.get('instrument', '')
        instrument_params = json_like.get('instrument_params', {})
        # Returns if array is empty
        if instrument_params == {}:
            print("Returning Blank")
            return encode_json({})
        instrument = get_instrument_by_name(instrument_name, instrument_params)

        # Gets the model and model params out of the dict
        model_name = json_like.get('model', '')
        model_params = json_like.get('model_params', {})
        model_params = {key: value.get('default', 0.0) for key, value in model_params.items()}
        model = get_model(model_name)

        # Gets slicer and Slicer params out of dict
        slicer_name = json_like.get('averaging_type', '')
        slicer_params = json_like.get('averaging_params', {})
        slicer_class = SLICER_MAP.get(slicer_name, Circular)
        slicer = slicer_class(slicer_params)

        calculator = Calculator(instrument, model, slicer)
        calculator.calculate(model_params)

        # Return all data
        return encode_json(calculator.format_data_for_return())

    @app.route('/calculate/model/<model_name>', methods=['POST'])
    def calculate_model(model_name: str) -> str:
        """Directly call the model calculation using a pre-defined API
        :return: A json-like string representation of a list of intensities.
        """
        data = decode_json(request.data)[0]
        json_like = json.loads(data)

        # Gets the model and model params out of the dict
        model_params = json_like.get('model_params', {})

        return encode_json(_calculate_model(model_name, model_params, None))

    def _calculate_model(model_name: str, model_params: Dict[str, Union[Number, str]],
                         q: Optional[List[np.ndarray]] = None) -> List[Number]:
        """Private method to directly call the model calculator
        :param model_name: The string representation of the model name used by sasmodels.
        :param model_params: A dictionary mapping the sasmodel parameter name to the parameter value.
        :param q: An n-dimensional array of Q values.
        :return: A json-like string representation of a list of intensities.
        """
        if q is None:
            # If no instrument data sent, use a default Q range of 0.0001 to 1.0 A^-1
            q = np.logspace(0.0001, 1.0, 125)
        return calculate_m(model_name, [q_i.flatten() for q_i in q], model_params)

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
