from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

import yabc


class TaxDoc(yabc.Base):
    __tablename__ = "taxdoc"
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    userid = Column(String)
    contents = Column(String)
