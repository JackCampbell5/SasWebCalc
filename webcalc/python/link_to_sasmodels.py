import json
import sys
from typing import Union, Dict, List

import numpy as np

from sasmodels.core import list_models, load_model
from sasmodels.direct_model import call_kernel

from .helpers import encode_json

Number = Union[float, int]


def get_model_list(category=None):
    """Gets the model list from sasmodels

    :param String category: A string value to be passed to the list models parameter in sasmodels
    :return: A list of the model list
    :rtype: List
    """
    return encode_json(list_models(category))


def get_structure_list(category=None):
    # models = list_models(category)
    # TODO find a way to get the models that have stucture factor, right now it is just found from the SasModels documentation
    structure_list = ["hardsphere","hayter_msa","squarewell","stickyhardsphere"]
    structure_list.insert(0,"None")
    return encode_json(structure_list)


def get_model(model_string):
    """Loads model params for the specified model

    :param str model_string:
    :return: A PyModel object that contains
    :rtype: PyModel
    """
    if not model_string:
        return None
    return load_model(model_string)


def encode_params(params):
    """Encodes the parameters gotten from sasmodels as a dictionary

    :param PyModel params: The pymodel object that contains the params
    :return: An encoded Json that contains the params encoded correctly
    :rtype: JSON or DllModel object
    """
    return_params = {}
    param_dict = {}
    for param in params:
        param_dict['units'] = str(param.units)
        param_dict['default'] = str(param.default)
        param_dict['lower_limit'] = str(param.limits[0])
        param_dict['upper_limit'] = str(param.limits[1])
        return_params[param.name] = param_dict.copy()
    return encode_json(return_params)


def get_all_params(model_string):
    """Gets all the params by passing True to the get params method

    :param str model_string: THe string name of the model
    :return: The list of params
    :rtype: list
    """
    return get_params(model_string, True)


def get_params(model_string, all=False):
    """Gets most of the params by passing False to the get params method

    :param str model_string: The string name of the model
    :param all: whether it is all the params or not
    :return: The list of the params encoded
    :rtype: list
    """
    model = get_model(model_string) if model_string else None
    if all and model:
        model = get_model(model_string)
        # Calls paramaters from sasmodels
        params = model.info.parameters.call_parameters
    elif model:
        params = model.info.parameters.common_parameters
        params.extend(model.info.parameters.kernel_parameters)
    else:
        params = []
    return encode_params(params)


def calculate_model(model_string: str, q: List[np.ndarray], params: Dict[str, float]) -> List[Number]:
    """ Takes the model and runs a sequence of code to calculate it

    :param str model_string: The string name of the model
    :param q: A list of numpy arrays with Q values that will be used to calculate the model function
    :param params: The list of params probably passed from a previous method
    :return: A list of calculated data from the model
    :rtype: A json-like string representation of a list of intensities.
    """
    kernel_model = get_model(model_string)
    kernel = kernel_model.make_kernel(q)
    i_q = call_kernel(kernel, params)
    # Use built-in numpy.where for value replacement
    i_q = np.where(i_q != np.inf, i_q, 9999999)
    i_q = np.where(~np.isnan(i_q), i_q, 8888888)
    # Return a list representation of the numpy array
    return i_q.tolist()


if __name__ == '__main__':
    model_string = sys.argv[1] if len(sys.argv) > 1 else 'sphere'
    q = np.logspace(-3, -1, 200)
    params = {}
    # Ensure a list of models is returned
    assert type(list_models()) is list
    # Ensure sphere model gives 5 basic params
    assert len(json.loads(get_params(model_string)).keys()) == 5
    # Ensure sphere model gives 14 total params, including orientation and dispersity params
    assert len(json.loads(get_all_params(model_string)).keys()) == 14
    # Ensure get_params(all=True) returns same as get_all_params()
    assert get_params(model_string, True) == get_all_params(model_string)
    assert type(json.loads(calculate_model(model_string, q, params))) is list
