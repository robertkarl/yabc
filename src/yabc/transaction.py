"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""
import datetime
import enum
from decimal import Decimal

import dateutil.parser
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator

import yabc

__author__ = "Robert Karl <robertkarljr@gmail.com>"


class PreciseDecimalString(TypeDecorator):
    impl = sqlalchemy.String

    def process_bind_param(self, value, dialect):
        """ Needs to return an object of the underlying impl 
        """
        return str(value)

    def process_result_value(self, value, dialect):
        if not value:
            value = 0
        return Decimal(value)


class TransactionOperationString(TypeDecorator):
    impl = sqlalchemy.String

    def process_bind_param(self, value, dialect):
        """ Needs to return an object of the underlying impl
        """
        assert isinstance(value, Transaction.Operation)
        return str(value.value)

    def process_result_value(self, value, dialect):
        """ Load from the DB and turn into an enum """
        if not value:
            value = Transaction.Operation.NOOP
        return Transaction.Operation(value)


class Transaction(yabc.Base):
    """
    Exchange-independent representation of a transaction (buy or sell)
    """

    @enum.unique
    class Operation(enum.Enum):
        NOOP = "Noop"
        BUY = "Buy"
        SELL = "Sell"
        GIFT = "Gift"
        SPLIT = "Split"

    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)
    asset_name = Column(sqlalchemy.String)
    date = Column(DateTime)
    fees = Column(PreciseDecimalString)
    operation = Column(TransactionOperationString)
    quantity = Column(PreciseDecimalString)
    source = Column(sqlalchemy.String)
    usd_subtotal = Column(PreciseDecimalString)
    user_id = Column(sqlalchemy.Integer, ForeignKey("user.id"))

    def __init__(
        self,
        asset_name,
        operation: Operation,
        date=None,
        fees=0,
        quantity=0,
        source=None,
        usd_subtotal=0,
        user_id="",
    ):
        assert date is not None
        for param in (quantity, fees, usd_subtotal):
            assert isinstance(param, (float, str, Decimal, int))
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
        operation = Transaction.Operation.BUY
        proceeds = json["Transfer Total"]
        fee = json["Transfer Fee"]
        asset_name = json["Currency"]
        quantity = Decimal(json["Amount"])
        if quantity < 0:
            operation = Transaction.Operation.SELL
            quantity = abs(quantity)
        timestamp_str = json["Timestamp"]
        return Transaction(
            asset_name=asset_name,
            operation=operation,
            quantity=quantity,
            date=dateutil.parser.parse(timestamp_str),
            fees=fee,
            source="coinbase",
            usd_subtotal=proceeds,
        )

    @staticmethod
    def gemini_type_to_operation(gemini_type: str):
        if gemini_type == "Buy":
            return Transaction.Operation.BUY
        elif gemini_type == "Sell":
            return Transaction.Operation.SELL
        raise RuntimeError(
            "Invalid Gemini transaction type {} encountered.".format(gemini_type)
        )

    @staticmethod
    def FromGeminiJSON(json):
        """
        Arguments
            json (Dictionary): 
        """

        operation = Transaction.gemini_type_to_operation(json["Type"])
        quantity = json["BTC Amount"]
        usd_total = json["USD Amount"]
        fee = json["USD Fee"]
        timestamp_str = "{}".format(json["Date"])
        return Transaction(
            asset_name="BTC",
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


def make_transaction(kind: Transaction.Operation, quantity, fees, subtotal):
    sample_date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
    return Transaction(
        "BTC",
        date=sample_date,
        operation=kind,
        fees=fees,
        quantity=quantity,
        usd_subtotal=subtotal,
    )
