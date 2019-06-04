from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

import yabc


class User(yabc.Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        self.password = password
