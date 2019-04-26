"""
Server that runs the REST endpoints and development server.
"""
import os
import sys

import flask
from flask import render_template

from yabc.server import sql_backend
from yabc.server.yabc_api import yabc_api

application = flask.Flask(__name__)

@application.route('/register')
def register():
    return render_template('register.html')

@application.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

def main():
    port = 5000
    if "YABC_DEBUG" in os.environ:
        application.debug = True
        print("listening on port {}".format(port))
    backend = sql_backend.SqlBackend()
    backend.create_tables()
    application.register_blueprint(yabc_api)
    print([i for i in application.url_map.iter_rules()])
    application.run(port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
