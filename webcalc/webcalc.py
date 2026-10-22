# Decides what to do based on link given
import importlib
import json
import mimetypes
import os
import sys

import numpy as np

from flask import Flask, render_template, request, send_file

# import specific methods from python files
from python.link_to_sasmodels import get_model_list, get_multiplicity_models, get_params, get_structure_list
from python.link_to_sasmodels import calculate_model as calculate_m
from python.link_to_sasmodels import get_model
from sasmodels.direct_model import call_kernel
from sasmodels.resolution import Pinhole1D
from python.helpers import decode_json, encode_json

Number = float | int


def create_app():
    app = Flask(__name__)
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')

    # Launches the main program based on a basic link
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/saswebcalc/', methods=['GET', 'POST'])
    def root() -> str:
        return render_template("index.html")

    # The documentation flask calls to get the documentation site to appear
    @app.route("/docs/<name>", methods=['GET', 'POST'])
    def docs_main(name) -> str:
        try:
            return render_template(f"docs/build/html/{name}")
        except Exception as e:
            print("Documentation Not Loaded ", str(e))
            return "Documentation Not Loaded Correctly"

    @app.route("/docs/api/<name>", methods=['GET', 'POST'])
    def docs_api(name) -> str:
        return render_template(f"docs/build/html/api/{name}")

    @app.route("/docs/_static/<name>", methods=['GET', 'POST'])
    def docs_static(name):
        return send_file(f"templates/docs/build/html/_static/{name}")

    @app.route("/docs/_static/css/<name>", methods=['GET', 'POST'])
    def docs_css(name):
        return send_file(f"templates/docs/build/html/_static/css/{name}")

    @app.route("/docs/_static/js/<name>", methods=['GET', 'POST'])
    def docs_js(name):
        return send_file(f"templates/docs/build/html/_static/js/{name}")

    @app.route("/docs/_static/css/fonts/<name>", methods=['GET', 'POST'])
    def docs_css_fonts(name):
        return send_file(f"templates/docs/build/html/_static/css/fonts/{name}")

    @app.route('/get/onLoad/', methods=['GET'])
    def get_all_onload() -> str:
        return_array = {}
        return_array["structures"] = get_structure_list()
        return_array["multiplicity_models"] = get_multiplicity_models()
        return_array["models"] = get_model_list()
        return_array["instruments"] = _get_all_instruments()
        return encode_json(return_array)

    def _get_all_instruments() -> dict[str: str]:
        """Gets a list of all the instruments that are in the python.instruments directory

        :return: A dictionary of the structure that includes structure name and the user visible name
        :rtype: Dict
        """
        instrument_list = {}
        loaded_instruments = _import_instruments()
        for instrument in loaded_instruments:
            cls = loaded_instruments[instrument]
            code_name = cls.class_name if hasattr(cls, "class_name") else str(cls)
            front_name = cls.name_shown if hasattr(cls, "name_shown") else code_name
            instrument_list[code_name] = front_name
        return instrument_list

    @app.route('/get/params/<model_name>', methods=['GET'])
    @app.route('/get/params/model/<model_name>', methods=['GET'])
    def get_model_params(model_name: str) -> str:
        params = get_params(model_name, json_encode=False)
        return _update_model_params(js_model_params=params)

    @app.route('/get/params/instrument/<instrument_name>', methods=['GET'])
    def get_instrument_params(instrument_name: str) -> str:
        loaded_instruments = _import_instruments()
        return encode_json(loaded_instruments[instrument_name].get_js_params())

    @app.route('/update/params/', methods=['POST'])
    def model_params_update() -> str:
        # Checks the params out differently if it is coming from the JS or the function
        data = decode_json(request.data)[0]
        json_like = json.loads(data)

        # Gets the model and model params out of the dict
        model = json_like.get('model', '')
        # Gets the model parameters form the JS
        js_model_params = json_like.get('model_params', {})
        if js_model_params is not dict:
            get_model_params(model_name=model)
        return _update_model_params(js_model_params=js_model_params)

    def _update_model_params(js_model_params=None) -> str:
        """Updates the model params to increasings the number of inputs if there is a multiplicity model

        :param dict js_model_params: A dictionary containing the parameters from the JS
        :return: An updated dictionary of the model params
        :rtype: Dict
        """

        if js_model_params is None:
            print("No Model Params")
            js_model_params = {}

        # Necessary Parameters
        new_model_params = {x: js_model_params[x] for x in js_model_params}  # A duplicate array of js_model_params
        param_keyword = ""  # The keyword that changes:
        first_run = True  # Is this the first run of the code
        model_params = [key for key in js_model_params]  # A list of just the name of model parameters

        # Find the keyword
        for num in range(len(model_params)):
            find = model_params[num].find('[')
            if find != -1:
                param_keyword = model_params[num][find + 1:model_params[num].find(']')]
                if param_keyword == '0':
                    param_keyword = model_params[num - 1]
                    first_run = False
                break

        # Return the array if there is no special keyword
        if param_keyword == "":
            return js_model_params

        # Remove all the params changed by the multiplicity models from the array
        sld_remove_dict = []
        for name in js_model_params:
            if '[' in name:
                sld_remove_dict.append(name)
        for name in sld_remove_dict:
            new_model_params.pop(name)

        # Move the param keyword to after all the non multiplicity model parameters
        new_model_params.pop(param_keyword)
        new_model_params[param_keyword] = js_model_params[param_keyword]

        # Finds the params and adds/removes them based on the param_keyword
        # Find the multiplicity model params
        sld_dict = []
        for name in js_model_params:
            if '[' in name and first_run:
                sld_dict.append(name)
            if not first_run:
                if '[' in name:
                    found = name.find('[')
                    sld_dict.append(name[0:found])

        # Add the correct number of multiplicity model params back to the result array
        for value in sld_dict:
            for num in range(int(js_model_params[param_keyword]["default"])):
                if first_run:
                    value_updated = value[0:value.find('[')] + '[' + str(num) + ']'
                    new_model_params[value_updated] = js_model_params[value]
                else:
                    value_updated = value + '[' + str(num) + ']'
                    if value_updated in js_model_params:
                        new_model_params[value_updated] = js_model_params[value_updated]
                    else:
                        new_model_params[value_updated] = js_model_params[value + "[0]"]
        return encode_json(new_model_params)

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
        structure_factor = json_like.get('structure_factor', 'None')
        is_structure_factor = True if structure_factor != 'None' else False
        model = json_like.get('model', '')
        if is_structure_factor:
            model = model + "@" + structure_factor
        model_params_base = json_like.get('model_params', {})
        model_params_base = _model_params_restructure(model_params_base)
        model_params = {}
        for k, v in model_params_base.items():
            try:
                model_params[k] = float(v)
            except ValueError:
                model_params[k] = v

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
        data_sets = list(params.get('data', {}).values())
        q_1d = [np.asarray(data_set['qValues']) for data_set in data_sets]
        sigma_q_1d = [np.asarray(data_set.get('sigmaQ', [])) for data_set in data_sets]
        q_2d = [np.asarray(data_set['q2DValues']) for data_set in data_sets]

        # Calculate the resolution smeared 1D model, then apply the beam stop shadowing factor
        model_1d = _calculate_model(model, model_params, q_1d, sigma_q_1d)
        for data_set, i_1d in zip(data_sets, model_1d):
            data_set['fSubs'] = (np.asarray(i_1d) * np.asarray(data_set['fSubs'])).tolist()
        # Calculate the 2D model (unsmeared)
        model_2d = _calculate_model(model, model_params, q_2d)
        for data_set, i_2d_model in zip(data_sets, model_2d):
            i_2d = np.asarray(data_set['intensity2D'])
            comb_2d = np.asarray(i_2d_model).reshape(i_2d.shape) * i_2d
            data_set['intensity2D'] = comb_2d.tolist()
        # Return all data
        return encode_json(params)

    def _model_params_restructure(model_params: dict[str: list[str]]) -> dict:
        """Restructures the parameters for the model calculations

        :param dict model_params: The model params to restructure
        :return: The restructured directory
        :rtype: Dict
        """
        model_params = {key: value.get('default', 0.0) for key, value in model_params.items()}
        results_dict = model_params.copy()
        for key, value in results_dict.items():
            if '[' in key:
                new_name = key[0:key.find('[')] + key[key.find('[') + 1:key.find(']')]
                model_params[new_name] = value
                model_params.pop(key)
        return model_params

    @app.route('/calculate/model/<model_name>', methods=['POST'])
    def calculate_model(model_name: str) -> str:
        """Directly call the model calculation using a pre-defined API
        :return: A json-like string representation of a list of intensities.
        """
        data = decode_json(request.data)[0]
        json_like = json.loads(data)

        # Gets the model and model params out of the dict
        model_params = json_like.get('model_params', {})

        return encode_json(_calculate_model(model_name, model_params, None)[0])

    def _calculate_model(model_name: str, model_params: dict[str, Number | str],
                         q: list[np.ndarray] | None = None,
                         sigma_q: list[np.ndarray] | None = None) -> list[list[Number]]:
        """Private method to directly call the model calculator
        :param model_name: The string representation of the model name used by sasmodels.
        :param model_params: A dictionary mapping the sasmodel parameter name to the parameter value.
        :param q: A list of Q arrays, one per detector panel/data set.
        :param sigma_q: An optional list of 1-sigma Q resolution arrays matching q. When given, the model is
            resolution smeared with a Gaussian (pinhole) resolution function.
        :return: A list (one entry per Q array) of lists of intensities.
        """
        if q is None:
            # If no instrument data sent, use a default Q range of 0.0001 to 1.0 A^-1
            q = [np.logspace(-4, 0, 125)]
        if sigma_q is None:
            sigma_q = [None] * len(q)
        # Each panel gets its own kernel so multi-panel instruments (VSANS) are not treated as N-dimensional Q
        return [_calculate_single_model(model_name, model_params, np.asarray(q_i).flatten(), dq_i)
                for q_i, dq_i in zip(q, sigma_q)]

    def _calculate_single_model(model_name: str, model_params: dict[str, Number | str], q: np.ndarray,
                                sigma_q: np.ndarray | None = None) -> list[Number]:
        """Calculate a model for a single Q array, applying pinhole smearing when a valid sigma_q is supplied."""
        if sigma_q is None or np.size(sigma_q) != np.size(q) or not np.any(np.asarray(sigma_q) > 0):
            return calculate_m(model_name, [q], model_params)
        sigma_q = np.asarray(sigma_q, dtype=float).flatten()
        sigma_q = np.where(np.isfinite(sigma_q) & (sigma_q > 0), sigma_q, 0.0)
        resolution = Pinhole1D(q, sigma_q)
        kernel = get_model(model_name).make_kernel([resolution.q_calc])
        i_q = resolution.apply(call_kernel(kernel, model_params))
        i_q = np.where(i_q != np.inf, i_q, 9999999)
        i_q = np.where(~np.isnan(i_q), i_q, 8888888)
        return i_q.tolist()

    @app.route('/calculate/instrument/<instrument_name>', methods=['POST'])
    def calculate_instrument(instrument_name: str) -> str:
        params = decode_json(request.data)
        # Calculates all the values and returns them
        return encode_json(_calculate_instrument(instrument_name, params))

    def _import_instruments() -> dict[str, dict]:
        """Gets a list of the instruments in the python.instruments directory

        :return: A dictionary that has the name and the object
        :rtype; Dict
        """
        # Imports all usable instruments which are then added to the instrument dict
        import python.instruments as instruments

        instruments_dict = {}
        for class_ in instruments.Instrument.__subclasses__():
            if class_.__name__ != "Example":
                instruments_dict[class_.__name__] = class_

        return instruments_dict

    def _calculate_instrument(instrument: str, params: dict) -> dict[str, Number | str | list[Number | str]]:
        """The base calculation script. Creates an instrument class, calculates the instrumental resolution for the
        configuration, and returns two list of intensities

        :param str instrument: The instrument that we're doing the calculations based off of
        :param dict params: A dictionary of parameters inputted by the user in the JavaScript
        :return: The python return dictionary
        :rtype: dict
        """
        loaded_instruments = _import_instruments()
        if instrument in loaded_instruments:
            loaded_instrument = loaded_instruments[instrument]
        else:
            print("Instrument Not on List")
            return {}
        # Temporary fix- TODO make the name of everything the same
        instrument_name = instrument[0:instrument.find("S")].lower()
        i_class = loaded_instrument(instrument_name, params)
        return i_class.sas_calc()

    return app


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    sas_calc = create_app()
    sas_calc.run(port=port, debug=True)


if __name__ == '__main__':
    main()
