from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

import yabc


class TaxDoc(yabc.Base):

    """
    TODO: Encrypt the contents. And probably the file names.
    """

    __tablename__ = "taxdoc"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    file_name = Column(String)
    file_hash = Column(String)
    exchange = Column(String)
    contents = Column(String)
