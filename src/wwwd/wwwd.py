"""
Server that runs the REST endpoints and development server.
"""
import os

import flask

from yabc.server import sql_backend
from yabc.server.yabc_api import yabc_api

application = flask.Flask(__name__)


def main():
    port = 5000
    if "YABC_DEBUG" in os.environ:
        application.debug = True
        print("listening on port {}".format(port))
    backend = sql_backend.SqlBackend()
    application.register_blueprint(yabc_api)
    application.run(port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
