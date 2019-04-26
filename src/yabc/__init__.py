import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(sqlalchemy.schema.ThreadLocalMetaData())
