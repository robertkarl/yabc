"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""
import datetime
import enum
from decimal import Decimal

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
        GIFT_RECEIVED = "GiftReceived"
        GIFT_SENT = "GiftSent"
        SPLIT = "Split"
        MINING = "Mining"
        SPENDING = "Spending"

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
        operation: Operation,
        asset_name="BTC",
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

    def is_input(self):
        """
        :return: True if this transaction is an input (like mining, a gift received, or a purchase)
        """
        return self.operation in {
            Operation.MINING,
            Operation.GIFT_RECEIVED,
            Operation.SPLIT,
            Operation.BUY,
        }

    def is_taxable_output(self):
        return self.operation in {Operation.SPENDING, Operation.SELL}

    def __repr__(self):
        return "<TX for user '{}': {} {} {asset_name} for {subtotal}, on {} from exchange {}. Fee {fee}.>".format(
            self.user_id,
            self.operation,
            self.quantity,
            self.date,
            self.source,
            asset_name=self.asset_name,
            subtotal=self.usd_subtotal,
            fee=self.fees,
        )


def make_transaction(
    kind: Transaction.Operation,
    quantity,
    fees,
    subtotal,
    date=datetime.datetime(2015, 2, 5, 6, 27, 56, 373000),
):
    return Transaction(
        operation=kind,
        asset_name="BTC",
        date=date,
        fees=fees,
        quantity=quantity,
        usd_subtotal=subtotal,
    )


Operation = Transaction.Operation
