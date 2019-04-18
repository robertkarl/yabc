from sqlalchemy import Column
from sqlalchemy import String

import yabc


class User(yabc.Base):
    __tablename__ = "user"
    user_id = Column(String, primary_key=True)
