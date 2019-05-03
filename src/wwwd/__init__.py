from flask import Flask
import os
import yabc.server.yabc_api
import yabc.server.sql_backend
from flask.cli import with_appcontext


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'yabc.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(yabc.server.yabc_api.bp)
    yabc.server.sql_backend.init_app(app)


    return app
