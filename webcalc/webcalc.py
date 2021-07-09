﻿import sys

from flask import Flask, render_template, request

from python.link_to_sasmodels import get_model_list, get_model


def create_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/saswebcalc/', methods=['GET', 'POST'])
    def root():
        if request.method == 'POST':
            # TODO: Write this
            pass
        elif request.method == 'GET':
            # TODO: Write this
            pass
        return render_template("index.html")

    @app.route('/getmodels/', methods=['GET'])
    def get_all_models():
        return get_model_list()

    @app.route('/calculatemodel/', methods=['GET'])
    def get_model_by_name(name):
        # TODO: This isn't correct...
        return get_model(name)

    @app.route('/getparams/', methods=['GET'])
    def get_model_params(name):
        return get_model_params(name)

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    app = create_app()
    app.run(port=port, debug=True)