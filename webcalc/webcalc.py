import sys

from flask import Flask, render_template, request

from python.link_to_sasmodels import get_model_list, get_model, get_params


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

    @app.route('/calculatemodel/<model_name>', methods=['GET'])
    def get_model_by_name(model_name):
        return get_model(model_name)

    @app.route('/getparams/<model_name>', methods=['GET'])
    def get_model_params(model_name):
        return get_params(model_name)

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    app = create_app()
    app.run(port=port, debug=True)