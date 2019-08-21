"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""
import datetime
import decimal
import enum
from decimal import Decimal

import sqlalchemy
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
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

@enum.unique
class Symbol(enum.Enum):
    BTC = enum.auto()
    ETH = enum.auto()
    BCH = enum.auto()
    USD = enum.auto()
    LTC = enum.auto()
    ZEC = enum.auto()




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
        TRADE_INPUT = "TradeInput"

    __tablename__ = "transaction"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    # Column "asset_name" deleted.
    date = sqlalchemy.Column(DateTime)
    fees = sqlalchemy.Column(PreciseDecimalString)
    fee_symbol = sqlalchemy.Column(sqlalchemy.String)
    operation = sqlalchemy.Column(TransactionOperationString)

    quantity_traded= sqlalchemy.Column(PreciseDecimalString) # column added
    symbol_traded = sqlalchemy.Column(sqlalchemy.String) # column added

    quantity_received = sqlalchemy.Column(PreciseDecimalString) # column added
    symbol_received = sqlalchemy.Column(sqlalchemy.String) # column added

    source = sqlalchemy.Column(sqlalchemy.String)
    usd_subtotal = sqlalchemy.Column(PreciseDecimalString) # deprecated
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("user.id"))

    def __init__(
        self,
        operation: Operation,
        date=None,
        fees=0,
        quantity_traded=0,
        source=None,
        quantity_received=0,
        user_id="",
            symbol_traded="",
            symbol_received="",
            fee_symbol="USD",
    ):
        for param in (quantity_traded, fees, quantity_received):
            assert isinstance(param, (float, str, Decimal, int))
        self.quantity_traded = Decimal(quantity_traded)
        self.symbol_traded = symbol_traded
        self.quantity_received = Decimal(quantity_received)
        self.symbol_received = symbol_received
        self.operation = operation
        if date:
            self.date = date.replace(tzinfo=None)
        self.quantity_received = Decimal(quantity_received)
        self.source = source
        self.user_id = user_id
        self.fees = decimal.Decimal(fees)
        self.fee_symbol = fee_symbol

    def is_to_fiat(self):
        return self.symbol_received == 'USD'

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
        elif self.operation == Operation.SELL and not self.is_to_fiat():
            # This means it was a BTC/ETH sale for example
            return True
        return False

    def is_taxable_output(self):
        return self.operation in {Operation.SPENDING, Operation.SELL}

    def __repr__(self):
        return "<{user} - {operation} {quantity_traded} {symbol_received} on {} for {quantity_received}, on {date} from {exchange}. Fee {fee}.>".format(
            exchange=self.source,
            date=self.date,
            operation=self.operation,
            quantity_traded=self.quantity_traded,
            user=self.user_id,
            asset_name=self.asset_name,
            quantity_received=self.quantity_received,
            fee=self.fees,
            symbol_received=self.symbol_received
        )


def make_transaction(
    kind: Transaction.Operation,
    quantity_received,
        symbol_received,
    quantity_traded,
    fees,
    date=datetime.datetime(2015, 2, 5, 6, 27, 56, 373000),
):
    return Transaction(
        operation=kind,
        date=date,
        fees=fees,
        quantity_traded=quantity_traded,
        symbol_received=symbol_received,
        quantity_received=quantity_received,
    )


Operation = Transaction.Operation
