"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"


from decimal import Decimal

import dateutil.parser
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

import yabc


class PreciseDecimalString(TypeDecorator):
    """
    TODO: see sqlalchemy docs on Column and data types > Custom Types > TypeDecorator recipes.
    """

    impl = String

    def process_bind_param(self, value, dialect):
        """ Needs to return an object of the underlying impl 
        """
        if isinstance(value, Decimal) and value.as_tuple()[2] < self.quantize_int:
            value = value.quantize(self.quantize)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, Decimal):
            value = Decimal(value)
        return value


class Transaction(yabc.Base):
    """
    Exchange-independent representation of a transaction (buy or sell)
    """

    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)
    asset_name = Column(String)
    date = Column(DateTime)
    fees = PreciseDecimalString(String)
    operation = Column(String)
    quantity = PreciseDecimalString(String)
    source = Column(String)
    usd_subtotal = PreciseDecimalString(String)
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
        for param in (quantity, fees, usd_subtotal):
            assert isinstance(param, (float, str, Decimal, int))
        assert quantity > 0
        self.quantity = Decimal(quantity)
        self.operation = operation
        self.date = date.replace(tzinfo=None)
        self.usd_subtotal = Decimal(usd_subtotal)
        self.source = source
        self.asset_name = asset_name
        self.user_id = user_id
        self.fees = Decimal(fees)

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
        quantity = json["BTC Amount"]
        usd_total = json["USD Amount"]
        fee = json["USD Fee"]
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
