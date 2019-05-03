import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(sqlalchemy.schema.ThreadLocalMetaData())

import yabc.server.yabc_api

bp = yabc.server.yabc_api.bp
