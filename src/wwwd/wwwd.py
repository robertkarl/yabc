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
    db_fname = os.path.join(application.instance_path, "cbr.sqlite")
    print(db_fname)
    backend = sql_backend.SqlBackend(db_fname)
    backend.create_tables()
    application.register_blueprint(yabc_api)
    application.run(port=port, host="0.0.0.0")


if __name__ == "__main__":
    print('hello')
    main()
