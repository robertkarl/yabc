"""
yabc HTTP endpoints are declared here.
"""
import os
import sys

import flask

from yabc.server import sql_backend
from yabc.server.yabc_api import yabc_api

application = flask.Flask(__name__)

HEADER_TEXT = """
    <html>\n<head> <title>yabc over HTTP</title> </head>\n<body>"""
footer_text = "</body>\n</html>"


def say_python_version():
    return "<p>Python version is {}.</p>\n".format(sys.version)


application.add_url_rule(
    "/", "index", (lambda: HEADER_TEXT + say_python_version() + footer_text)
)


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
