import sys

import numpy as np
from flask import Flask, render_template, request

from python.link_to_sasmodels import get_model_list, get_params
from python.link_to_sasmodels import calculate_model as calculate
from python.helpers import decode_json


def create_app():
    app = Flask(__name__)

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
        q = np.array(data[0][2])
        param_names = data[0][0]
        param_values = data[0][1]
        if len(data) > 3:
            q = np.array([data[0][2], data[0][3]])
        params = {param_names[i]: param_values[i] for i in range(len(param_values))}
        return calculate(model_name, q, params)

    @app.route('/getparams/<model_name>', methods=['GET'])
    def get_model_params(model_name):
        return get_params(model_name)

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    app = create_app()
    app.run(port=port, debug=True)