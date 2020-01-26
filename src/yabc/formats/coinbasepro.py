import csv
import datetime
import decimal

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

_DATE_HEADER = "created at"
_SIZE_HEADER = "size"
_SIZE_UNITS_HEADER = "size unit"
_FEE_HEADER = "fee"
_UNITS_HEADER = "price/fee/total unit"
_MARKET_HEADER = "product"
_ORDER_TYPE_HEADER = "side"
_TOTAL_HEADER = "total"

_HEADERS = [
    "portfolio",
    "trade id",
    _MARKET_HEADER,
    _ORDER_TYPE_HEADER,
    _DATE_HEADER,
    _SIZE_HEADER,
    _SIZE_UNITS_HEADER,
    "price",
    "fee",
    _TOTAL_HEADER,
    _UNITS_HEADER,
]


_KNOWN_COINS = {
    "ADA",
    "ADX",
    "ALGO",
    "AMB",
    "AST",
    "ATOM",
    "BAT",
    "BCH",
    "BCPT",
    "BNB",
    "BSV",
    "CVC",
    "BTC",
    "DASH",
    "DNT",
    "ENG",
    "EOS",
    "ETC",
    "ETH",
    "FTT",
    "GVT",
    "ICX",
    "IOTA",
    "LINK",
    "LTC",
    "LUN",
    "LOOM",
    "MANA",
    "MOD",
    "MTL",
    "NANO",
    "NEO",
    "ONT",
    "PPT",
    "TOMO",
    "TRX",
    "USDT",
    "XLM",
    "XRP",
    "XTZ",
}


_TYPE_MAP = {"SELL": transaction.Operation.SELL, "BUY": transaction.Operation.BUY}


class CoinbaseProMarket:
    """ BTC-USD for example
    """

    def __init__(self, market_name: str):
        self._first, self._second = market_name.split("-")

    def first(self):
        return self._first

    def second(self):
        return self._second


class FinancialQuantity:
    def __init__(self, quantity, unit):
        assert type(unit) == str
        assert type(quantity) == decimal.Decimal
        self.quantity = quantity
        self.unit = unit

    def is_fiat(self):
        return transaction.is_fiat(self.unit)

    def __repr__(self):
        return "<{} {}>".format(self.quantity, self.unit)


def _make_transaction(
    date: datetime.datetime,
    market: CoinbaseProMarket,
    operation: transaction.Operation,
    leg1: FinancialQuantity,
    leg2: FinancialQuantity,
    fee: FinancialQuantity,
):
    # The following fields are accurate if the tx is a BUY and not coin/coin.
    is_coin_to_coin = not leg1.is_fiat() and not leg2.is_fiat()
    if operation == transaction.Operation.BUY and is_coin_to_coin:
        operation = transaction.Operation.SELL
        # Swap all of these, and the operation
        tmp = leg1
        leg1 = leg2
        leg2 = tmp

    return transaction.Transaction(
        operation=operation,
        source=_EXCHANGE_ID_STR,
        quantity_traded=quantity_traded,
        quantity_received=quantity_received,
        symbol_traded=symbol_traded,
        symbol_received=symbol_received,
        date=date,
        fees=fee,
        fee_symbol=feecoin,
    )


def _raise_if_headers_bad(row):
    for header in _HEADERS:
        if header not in row:
            raise RuntimeError("Not a valid Coinbase Pro/Prime file.")


def _tx_from_row(line):
    date = delorean.parse(line[_DATE_HEADER], dayfirst=False).datetime
    market = CoinbaseProMarket(line[_MARKET_HEADER])
    operation = _TYPE_MAP[line[_ORDER_TYPE_HEADER]]
    leg1 = FinancialQuantity(
        abs(decimal.Decimal(line[_SIZE_HEADER])), line[_SIZE_UNITS_HEADER]
    )
    leg2 = FinancialQuantity(
        abs(decimal.Decimal(line[_TOTAL_HEADER])), line[_UNITS_HEADER]
    )
    fee = FinancialQuantity(decimal.Decimal(line[_FEE_HEADER]), line[_UNITS_HEADER])
    return _make_transaction(date, market, operation, leg1, leg2, fee)


def _read_txs_from_file(f):
    ans = []
    f.seek(0)
    contents = csv.DictReader(f)
    checked_headers = False
    for row in contents:
        if not checked_headers:
            _raise_if_headers_bad(row)
            checked_headers = True
        item = _tx_from_row(row)
        if item is not None:
            ans.append(item)
    return ans


class CoinbaseProParser(Format):
    EXCHANGE_HUMAN_READABLE_NAME = "Coinbase Pro/Prime"
    _EXCHANGE_ID_STR = "coinbasepro"

    def parse(self):
        self._reports = _read_txs_from_file(self._file)

    def __init__(self, file=None, filename: str = None):
        self._file = file
        self._reports = []
        self._filename = filename
        self.parse()
        self.cleanup()

    def __next__(self):
        if not self._reports:
            raise StopIteration
        return self._reports.pop(0)

    def __iter__(self):
        return self


FORMAT_CLASSES.append(CoinbaseProParser)
