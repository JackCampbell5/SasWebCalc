import logging
import pkg_resources
import sys
import traceback

from flask import Flask, make_response, render_template
import msgpack as msgpack_converter
from werkzeug.exceptions import HTTPException


def create_app():

    # FIXME: Find the proper location for js files

    app = Flask(__name__)

    @app.route('/saswebcalc/')
    def root():
        return render_template("index.html")

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    app = create_app()
    app.run(port=port, debug=True)