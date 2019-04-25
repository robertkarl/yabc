from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

Base = declarative_base(sqlalchemy.schema.ThreadLocalMetaData())
