"""
yabc HTTP endpoints are declared here.
"""
import os
import sys
import sqlalchemy

import flask

from yabc.server import sql_backend

application = flask.Flask(__name__)

HEADER_TEXT = """
    <html>\n<head> <title>yabc over HTTP</title> </head>\n<body>"""
footer_text = "</body>\n</html>"


def say_python_version():
    return "<p>Python version is {}.</p>\n".format(sys.version)


application.add_url_rule(
    "/", "index", (lambda: HEADER_TEXT + say_python_version() + footer_text)
)


@application.route("/yabc/v1/run_basis", methods=["POST"])
def run_basis():
    userid = flask.request.args.get('userid')
    backend = sql_backend.SqlBackend()
    return backend.run_basis(userid)


@application.route("/yabc/v1/taxdocs", methods=["POST"])
def taxdoc_create():
    print(dir(sqlalchemy.dialects))
    exchange = flask.request.args.get('exchange')
    userid = flask.request.args.get('userid')
    submitted_stuff = flask.request.get_data()
    backend = sql_backend.SqlBackend()
    return backend.taxdoc_create(exchange, userid, submitted_stuff)


@application.route("/transactions", methods=["POST"])
def add_tx():
    userid = flask.request.args.get('userid')
    tx = flask.request.get_data()
    backend = sql_backend.SqlBackend()
    return backend.add_tx(userid, tx)


# User

@application.route("/yabc/v1/users/<userid>", methods=["GET"])
def user_read(userid):
    backend = sql_backend.SqlBackend()
    return backend.user_read(userid)

@application.route("/yabc/v1/users", methods=["POST"])
def user_create():
    name = flask.request.args.get('name')
    backend = sql_backend.SqlBackend()
    return backend.user_create(name)


def main():
    port = 5000
    if "YABC_DEBUG" in os.environ:
        application.debug = True
        print("listening on port {}".format(port))
    backend = sql_backend.SqlBackend()
    backend.create_tables()
    application.run(port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
