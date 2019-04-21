"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"


import dateutil
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

import yabc


class Transaction(yabc.Base):
    """
    Exchange-independent representation of a transaction (buy or sell)
    """

    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user.user_id"))
    asset_name = Column(String)
    quantity = Column(Float)
    date = Column(DateTime)
    operation = Column(String)
    source = Column(String)
    usd_subtotal = Column(Float)
    fees = Column(Float)

    def __init__(
        self,
        operation=None,
        quantity=0,
        date=None,
        proceeds=0,
        source=None,
        fees=0,
        asset_name="BTC",
    ):
        assert operation in ["Buy", "Sell"]
        assert date is not None
        assert type(quantity) is float
        assert quantity > 0
        self.quantity = quantity
        self.operation = operation
        self.date = date.replace(tzinfo=None)
        self.usd_subtotal = proceeds
        self.source = source
        self.asset_name = "BTC"

    @staticmethod
    def FromCoinbaseJSON(json):
        """
        Arguments:
            json (dict): a coinbase-style dictionary with the following fields:
                - 'Transfer Total': the total price, including fees.
                - 'Transfer Fee': the fee charged by the exchange.
                - 'Amount': the amount of bitcoin sold. (It's negative for
                  sales.)
                - 'Timestamp': 'hour:min:sec.millisecs' formatted timestamp.
        Returns: Transaction instance with important fields populated
        """
        operation = "Buy"
        proceeds = float(json["Transfer Total"])
        fee = float(json["Transfer Fee"])
        quantity = float(json["Amount"])
        if quantity < 0:
            operation = "Sell"
            quantity = abs(quantity)
        timestamp_str = json["Timestamp"]
        return Transaction(
            operation,
            quantity=quantity,
            date=dateutil.parser.parse(timestamp_str),
            fees=fee,
            source="coinbase",
            proceeds=proceeds,
        )

    @staticmethod
    def FromGeminiJSON(json):
        """
        Arguments
            json (Dictionary): 
        """
        operation = json["Type"]
        quantity = float(json["BTC Amount"])
        usd_total = float(json["USD Amount"])
        fee = float(json["USD Fee"])
        assert fee >= 0  # Fee can round to zero for small txs
        assert unit_price > 0
        timestamp_str = "{}".format(json["Date"])
        return Transaction(
            operation,
            quantity=quantity,
            fees=fee,
            date=dateutil.parser.parse(timestamp_str),
            source="gemini",
            proceeds=usd_total,
        )

    def __repr__(self):
        return "<TX for {}: {} {} BTC @ {}, on {} from exchange {}>".format(
            self.user_id,
            self.operation,
            self.quantity,
            self.usd_subtotal,
            self.date,
            self.source,
        )
