"""
yabc HTTP endpoints are declared here.
"""
import hashlib
import json
import os
import sys
import tempfile

import flask

from yabc import basis
from yabc.server import inmemory_backend

application = flask.Flask(__name__)


BACKEND_ENV_KEY = "COINSAPI_BACKEND"
INMEMORY_BACKEND_ENV_VALUE = "inmemory"

COINS_USER_DATA_BUCKET = "coins8949-userdata"


HEADER_TEXT = """
    <html>\n<head> <title>yabc over HTTP</title> </head>\n<body>"""
footer_text = "</body>\n</html>"


backend = None


def set_backend():
    """
    Search order:
        1) environment variable 'COINSAPI_BACKEND'
    If not set, then use the inmemory backend.
    """
    global backend
    if BACKEND_ENV_KEY in os.environ:
        backend_str = os.environ[BACKEND_ENV_KEY]
        if backend_str == INMEMORY_BACKEND_ENV_VALUE:
            backend = inmemory_backend
            print("in memory backend chosen")
    if not backend:
        print("Defaulted to inmemory backend")
        backend = inmemory_backend


def get_backend():
    return backend


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
    set_backend()
    application.run(port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
