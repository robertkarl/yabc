import os

from flask import Flask

import yabc.server.sql_backend
import yabc.server.yabc_api


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "yabc.sqlite")
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(yabc.server.yabc_api.bp)
    yabc.server.sql_backend.init_app(app)

    return app
