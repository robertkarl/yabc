import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(sqlalchemy.schema.ThreadLocalMetaData())

import yabc.server.yabc_api  # isort:skip

bp = yabc.server.yabc_api.bp
