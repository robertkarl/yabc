"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""
import datetime
import enum
from decimal import Decimal

import sqlalchemy
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
        if not value or value == "None":
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
    """
    Note that we don't use auto() because it's not in python3.5
    """

    BTCUSD = 1
    ETHUSD = 2
    BCHUSD = 3
    ZECUSD = 4
    LTCUSD = 5
    BTCETH = 6


@enum.unique
class Symbol(enum.Enum):
    """
    These aren't in wide use yet.
    TODO: Migrate to use these instead of strings.
    """

    BTC = 1
    ETH = 2
    BCH = 3
    USD = 4
    LTC = 5
    ZEC = 6


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
    asset_name = sqlalchemy.Column(sqlalchemy.String)  # Deprecated
    quantity = sqlalchemy.Column(PreciseDecimalString)  # Deprecated
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    fees = sqlalchemy.Column(PreciseDecimalString)
    fee_symbol = sqlalchemy.Column(sqlalchemy.String)  # new in schema 8
    operation = sqlalchemy.Column(TransactionOperationString)

    quantity_traded = sqlalchemy.Column(PreciseDecimalString)  # column added
    symbol_traded = sqlalchemy.Column(sqlalchemy.String)  # column added

    quantity_received = sqlalchemy.Column(PreciseDecimalString)  # column added
    symbol_received = sqlalchemy.Column(sqlalchemy.String)  # column added

    source = sqlalchemy.Column(sqlalchemy.String)
    usd_subtotal = sqlalchemy.Column(PreciseDecimalString)  # deprecated
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))

    def __init__(
        self,
        operation: Operation,
        asset_name="BTC",  # deprecated
        date=None,
        fees=0,
        quantity=0,
        source=None,
        usd_subtotal=0,  # depreacted
        user_id="",
        symbol_traded="",
        symbol_received="",
        quantity_traded=0,
        quantity_received=0,
        fee_symbol="USD",
    ):
        for param in (quantity, fees, usd_subtotal):
            assert isinstance(param, (float, str, Decimal, int))
        self.quantity = Decimal(quantity)
        self.operation = operation
        self.date = date
        if date and isinstance(date, datetime.datetime):
            self.date = date.replace(tzinfo=None)
        self.usd_subtotal = Decimal(usd_subtotal)
        self.source = source
        self.asset_name = asset_name
        self.user_id = user_id
        self.fees = Decimal(fees)

        # The new syntax explicitly labels each leg of the trade.
        # Allow its use to overwrite values in columns for "asset_name" and "usd_subtotal"
        self.quantity_received = Decimal(quantity_received)
        self.quantity_traded = Decimal(quantity_traded)
        self.fee_symbol = fee_symbol
        self.symbol_received = symbol_received
        self.symbol_traded = symbol_traded

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
