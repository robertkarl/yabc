import os

from flask import Flask

import yabc.server.sql_backend
import yabc.server.yabc_api
from yabc import ohlcprovider


def create_app(test_config=None):
    """
    Generate the flask app. Which database to use, highest priority first:

    1) any DATABASE value set in test_config 
    2) any DATABASE value set in config.py
    3) sqlite:///{app.instance_path}/yabc.sqlite

    """

    app = Flask(__name__, instance_relative_config=True)
    app.ohlc = ohlcprovider.OhlcProvider()
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE="sqlite:///{}".format(os.path.join(app.instance_path, "yabc.sqlite")),
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
