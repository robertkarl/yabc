"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"


import dateutil.parser
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
    asset_name = Column(String)
    date = Column(DateTime)
    fees = Column(Float)
    operation = Column(String)
    quantity = Column(Float)
    source = Column(String)
    usd_subtotal = Column(Float)
    user_id = Column(String, ForeignKey("user.id"))

    def __init__(
        self,
        asset_name="BTC",
        date=None,
        fees=0,
        operation=None,
        quantity=0,
        source=None,
        usd_subtotal=0,
        user_id="",
    ):
        assert operation in ["Buy", "Sell"]
        assert date is not None
        assert type(quantity) is float
        assert quantity > 0
        self.quantity = quantity
        self.operation = operation
        self.date = date.replace(tzinfo=None)
        self.usd_subtotal = usd_subtotal
        self.source = source
        self.asset_name = asset_name
        self.user_id = user_id
        self.fees = fees

    @staticmethod
    def FromCoinbaseJSON(json):
        """
        Arguments:
            json (dict): a coinbase-style dictionary with the following fields:
                - 'Transfer Total': the total USD price, including fees.
                - 'Transfer Fee': the USD fee charged by the exchange.
                - 'Amount': the amount of bitcoin sold. (It's negative for sales.)
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
            operation=operation,
            quantity=quantity,
            date=dateutil.parser.parse(timestamp_str),
            fees=fee,
            source="coinbase",
            usd_subtotal=proceeds,
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
        timestamp_str = "{}".format(json["Date"])
        return Transaction(
            operation=operation,
            quantity=quantity,
            fees=fee,
            date=dateutil.parser.parse(timestamp_str),
            source="gemini",
            usd_subtotal=usd_total,
        )

    def __repr__(self):
        return "<TX for user '{}': {} {} BTC @ {}, on {} from exchange {}. Fee {}.>".format(
            self.user_id,
            self.operation,
            self.quantity,
            self.usd_subtotal,
            self.date,
            self.source,
            self.fees,
        )
