import json
import sys

from numpy import logspace

from sasmodels.core import list_models, load_model
from sasmodels.direct_model import call_kernel

from helpers import encode_json


def get_model_list(category=None):
    return encode_json(list_models(category))


def get_model(model_string):
    if not model_string:
        return None
    return load_model(model_string)


def calculate_model(model_string, q, params):
    pars = json.loads(params)
    kernel_model = get_model(model_string)
    kernel = kernel_model.make_kernel([q])
    Iq = call_kernel(kernel, pars)
    return json.dumps(Iq.tolist())


if __name__ == '__main__':
    model_string = sys.argv[1] if len(sys.argv) > 1 else 'sphere'
    q = logspace(-3, -1, 200)
    params = '{}'
    print(list_models())
    print(calculate_model(model_string, q, params))
