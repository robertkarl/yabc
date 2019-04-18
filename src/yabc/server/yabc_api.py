"""
yabc HTTP endpoints are declared here.
"""
import os
import sys

import flask

from yabc.server import sql_backend

application = flask.Flask(__name__)

HEADER_TEXT = """
    <html>\n<head> <title>yabc over HTTP</title> </head>\n<body>"""
footer_text = "</body>\n</html>"


_backend = None


def get_backend():
    global _backend
    if not _backend:
        _backend = sql_backend.SqlBackend()
    print('created a new backend')
    return _backend


def say_python_version():
    return "<p>Python version is {}.</p>\n".format(sys.version)


# add a rule for the index page.
application.add_url_rule(
    "/", "index", (lambda: HEADER_TEXT + say_python_version() + footer_text)
)

##########################################################################
# Begin endpoint declarations
#
endpoints = []


@application.route("/run_basis/<userid>", methods=["POST"])
def run_basis(userid):
    return get_backend().run_basis(userid)


endpoints.append(run_basis)


@application.route("/add_document/<exchange>/<userid>", methods=["POST"])
def add_document(exchange, userid):
    return get_backend().add_document(exchange, userid)


@application.route("/add_tx/<userid>", methods=["POST"])
def add_tx(userid):
    return get_backend().add_tx(userid)


@application.route("/add_user/<userid>", methods=["POST"])
def add_user(userid):
    return get_backend().add_user(userid)


endpoints.append(add_document)

#
# End endpoint decls
############################################################################


def main():
    port = 5000
    if "YABC_DEBUG" in os.environ:
        application.debug = True
        print("endpoints are: {}".format(list(x.__name__ for x in endpoints)))
        print("listening on port {}".format(port))
    application.run(port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
