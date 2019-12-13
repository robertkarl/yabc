import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

from . import server
from . import version

Base = declarative_base(sqlalchemy.schema.ThreadLocalMetaData())

import yabc.server.yabc_api  # isort:skip

bp = yabc.server.yabc_api.bp

api = server.yabc_api
get_db = server.sql_backend.get_db
__version__ = version.__version__
