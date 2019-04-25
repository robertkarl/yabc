from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

import yabc


class User(yabc.Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
