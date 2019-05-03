import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

import yabc.server.yabc_api

Base = declarative_base(sqlalchemy.schema.ThreadLocalMetaData())

bp = yabc.server.yabc_api.bp
