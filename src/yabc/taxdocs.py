import dateutil
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import sessionmaker

import yabc


class TaxDoc(yabc.Base):
    __tablename__ = "taxdoc"
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    userid = Column(String)
    contents = Column(String)
