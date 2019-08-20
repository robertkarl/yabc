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

@enum.unique
class Market(enum.Enum):
    BTCUSD = enum.auto()
    ETHUSD = enum.auto()
    BCHUSD = enum.auto()
    ZECUSD = enum.auto()
    LTCUSD = enum.auto()
    BTCETH = enum.auto()


class Transaction(yabc.Base):
    """
    Exchange-independent representation of a transaction (buy or sell).

    Each transaction is something that the user actually clicked a button to do. For example, trading BTC for ETH is one
    transaction.

    On Binance, a single trade can result in several events that affect taxes. Consider the BTCETH market, and a single SELL order executed there:
    - coins can be used to pay fees. this means the coins need to be subtracted from the pool.
    - BTC needs to be removed from the pool
    - ETH needs to be added (less fees)
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
    # Column asset_name deleted.
    market_name = Column(sqlalchemy.String) # column added example: "BTCUSD"
    date = Column(DateTime)
    fees = Column(PreciseDecimalString)
    operation = Column(TransactionOperationString)
    first_quantity= Column(PreciseDecimalString) # column added
    second_quantity = Column(PreciseDecimalString) # column added
    source = Column(sqlalchemy.String)
    usd_subtotal = Column(PreciseDecimalString) # deprecated
    user_id = Column(sqlalchemy.Integer, ForeignKey("user.id"))

    def __init__(
        self,
        operation: Operation,
        market: Market=Market.BTCUSD,
        date=None,
        fees=0,
        first_quantity=0,
        source=None,
        second_quantity=0,
        user_id="",
    ):
        for param in (first_quantity, fees, second_quantity):
            assert isinstance(param, (float, str, Decimal, int))
        self.first_quantity = Decimal(first_quantity)
        self.operation = operation
        if date:
            self.date = date.replace(tzinfo=None)
        if not market in Market:
            raise RuntimeError("Unsuppored market {}".format(market))
        self.second_quantity = Decimal(second_quantity)
        self.source = source
        self.market_name = market.name
        self.user_id = user_id
        self.fees = Decimal(fees)

    def to_fiat(self):
        return 'USD' in self.market_name

    def is_input(self):
        """
        :return: True if this transaction is an input (like mining, a gift received, or a purchase)
        """
        if self.operation in {
            Operation.MINING,
            Operation.GIFT_RECEIVED,
            Operation.SPLIT,
            Operation.BUY,
        }:
            return True
        elif self.operation == Operation.SELL and not self.to_fiat():
            # This means it was a BTC/ETH sale for example
            return True
        return False

    def is_taxable_output(self):
        return self.operation in {Operation.SPENDING, Operation.SELL}

    def __repr__(self):
        return "<{user} - {operation} {first} on {market} for {second}, on {date} from {exchange}. Fee {fee}.>".format(
            exchange=self.source,
            date=self.date,
            operation=self.operation,
            market = self.market_name,
            first=self.first_quantity,
            user=self.user_id,
            asset_name=self.asset_name,
            second=self.second_quantity,
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
        market=Market.BTCUSD,
        date=date,
        fees=fees,
        first_quantity=quantity,
        second_quantity=subtotal,
    )


Operation = Transaction.Operation
