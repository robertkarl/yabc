"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""
import datetime
import enum
from decimal import Decimal

import sqlalchemy.orm
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


def is_fiat(symbol):
    return symbol == "USD"


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
        MINING = "Mining"
        SPENDING = "Spending"
        # The following aren't stored in the DB, put typically only used in basis calculations as temporary values.
        TRADE_INPUT = "TradeInput"
        SPLIT = "Split"

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
        usd_subtotal=0,  # deprecated
        user_id="",
        symbol_traded="",
        symbol_received="",
        quantity_traded=0,
        quantity_received=0,
        fee_symbol="USD",
        triggering_transaction=None,
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
        self.triggering_transaction = triggering_transaction

        # The new syntax explicitly labels each leg of the trade.
        # Allow its use to overwrite values in columns for "asset_name" and "usd_subtotal"
        self.quantity_received = Decimal(quantity_received)
        self.quantity_traded = Decimal(quantity_traded)
        self.fee_symbol = fee_symbol
        self.symbol_received = symbol_received
        self.symbol_traded = symbol_traded

        if symbol_received or symbol_traded:
            # Both must be specified.
            # Quantity can't be used.
            # Try to populate the old fields.
            assert symbol_received and symbol_traded
            assert not quantity
            if self.is_simple_input():
                self.quantity = quantity_received
                self.asset_name = symbol_received
                self.usd_subtotal = quantity_traded
            else:
                # We're disposing of the asset.
                self.asset_name = symbol_traded
                self.usd_subtotal = quantity_received
                self.quantity = quantity_traded

        self.init_on_load()
        assert self.quantity_traded or self.quantity_received

    def is_coin_to_coin(self):
        if self.operation in {
            Operation.MINING,
            Operation.GIFT_SENT,
            Operation.GIFT_RECEIVED,
            Operation.SPLIT,
        }:
            return False
        if self.operation in {Operation.BUY, Operation.SELL}:
            return not is_fiat(self.symbol_traded) and not is_fiat(self.symbol_received)

    def needs_migrate_away_from_asset_name(self):
        return self.symbol_received == "" and self.symbol_traded == ""

    @sqlalchemy.orm.reconstructor
    def init_on_load(self):
        """
        Restore fields from self.asset_name and self.quantity to the more general columns.
        """
        if not self.needs_migrate_away_from_asset_name():
            # Do not modify the object further if we've already restored fields.
            return

        self.fee_symbol = (
            "USD"
        )  # Not possible to have others, until binance or other coin/coin markets are added.
        if self.is_simple_input():
            self.symbol_received = self.asset_name
            self.quantity_received = self.quantity
            self.symbol_traded = "USD"
            self.quantity_traded = self.usd_subtotal
        else:
            # Check the assumption that there are no SPLITs in the DB.
            assert self.operation in {
                Transaction.Operation.SPENDING,
                Transaction.Operation.GIFT_SENT,
                Transaction.Operation.SELL,
            }
            # We assume that these are SELLs in the sense that we are trading away BTC and receiving cash.
            self.symbol_traded = self.asset_name
            self.quantity_traded = self.quantity
            self.symbol_received = "USD"
            self.quantity_received = self.usd_subtotal

    def is_simple_input(self):
        return self.operation in {
            Operation.MINING,
            Operation.GIFT_RECEIVED,
            Operation.SPLIT,
            Operation.BUY,
            Operation.TRADE_INPUT,
        }

    def trade_has_input(self):
        """
        TODO: coin/coin trades make this more complicated, as SELLs can also be inputs.
        :return: True if this transaction is an input (like mining, a gift received, or a purchase)
        """
        if self.operation in {
            Operation.MINING,
            Operation.GIFT_RECEIVED,
            Operation.SPLIT,
            Operation.BUY,
            Operation.TRADE_INPUT,
        }:
            return True
        if self.Operation == Operation.SELL:
            return self.is_coin_to_coin()
        return False

    def is_taxable_output(self):
        return self.operation in {Operation.SPENDING, Operation.SELL}

    def __repr__(self):
        return "<TX {date} {operation} {rcvd} {rcvd_symbol} for {traded} {traded_symbol}, from exchange {source}. Fee {fee} {feecoin}>".format(
            date=self.date,
            traded=self.quantity_traded,
            traded_symbol=self.symbol_traded,
            rcvd=self.quantity_received,
            rcvd_symbol=self.symbol_received,
            operation=self.operation.name,
            source=self.source,
            fee=self.fees,
            feecoin=self.fee_symbol,
        )


Operation = Transaction.Operation
