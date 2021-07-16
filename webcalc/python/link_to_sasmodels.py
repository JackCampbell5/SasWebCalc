import json
import sys

import numpy as np

from sasmodels.core import list_models, load_model
from sasmodels.direct_model import call_kernel

from .helpers import encode_json


def get_model_list(category=None):
    return encode_json(list_models(category))


def get_model(model_string):
    if not model_string:
        return None
    return load_model(model_string)


def encode_params(params):
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
    return get_params(model_string, True)


def get_params(model_string, all=False):
    model = get_model(model_string) if model_string else None
    if all and model:
        model = get_model(model_string)
        params = model.info.parameters.call_parameters
    elif model:
        params = model.info.parameters.common_parameters
        params.extend(model.info.parameters.kernel_parameters)
    else:
        params = []
    return encode_params(params)


def calculate_model(model_string, q, params):
    kernel_model = get_model(model_string)
    kernel = kernel_model.make_kernel(q)
    Iq = call_kernel(kernel, params)
    return json.dumps(Iq.tolist())


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
