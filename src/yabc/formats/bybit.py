"""
yabc is not affiliated with the exchange or company bybit.

Format notes: Real Sell trades have 'BUY' type and an order type (limit, market)
"""
import decimal
from typing import Sequence

import delorean
import openpyxl
from openpyxl.cell import Cell

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format
from yabc.transaction import Operation

_KNOWN_COINS = {"BTC", "EOS", "ETH", "XRP"}

_BYBIT_HEADERS = [
    "Symbol",
    "Side",
    "Exec Type",
    "Exec Qty",
    "Exec Price",
    "Exec Value",
    "Fee Rate",
    "Fee",
    "Order Price",
    "Leaves Qty",
    "Order Type",
    "Transaction ID",
    "Order#",
    "Time(UTC)",
]


_TYPE_MAP = {"Sell": transaction.Operation.SELL, "Buy": transaction.Operation.BUY}

_EXCHANGE_ID_STR = "bybit"


def _transaction_from_dict(
    market, operation, usd, _, crypto_quantity, fee_in_crypto, date
):
    # The following fields are accurate if the tx is a BUY and not coin/coin.
    if operation == Operation.BUY:
        symbol_traded = "USD"
        symbol_received = market
        quantity_traded = usd
        quantity_received = crypto_quantity
    elif operation == Operation.SELL:
        symbol_received = "USD"
        symbol_traded = market
        quantity_received = usd
        quantity_traded = crypto_quantity
    # No coin/coin markets here
    return transaction.Transaction(
        operation=operation,
        source=_EXCHANGE_ID_STR,
        quantity_traded=quantity_traded,
        quantity_received=quantity_received,
        symbol_traded=symbol_traded,
        symbol_received=symbol_received,
        date=date,
        fees=decimal.Decimal(0),
        fee_symbol="USD",
    )


def _raise_if_headers_bad(row):
    for i, h in enumerate(_BYBIT_HEADERS):
        if not row[i].value == h:
            raise RuntimeError(
                "Not a valid Bybit valid, header {} found".format(row[i].value)
            )


def _tx_from_bybit_row(line: Sequence[Cell]):
    """
    Just extract the data from the correct columns
    """
    market = line[0].value[:3]
    if line[1].value in _TYPE_MAP:
        operation = _TYPE_MAP[line[1].value]
    else:
        return None
    usd = decimal.Decimal(line[3].value)
    price_in_fiat = decimal.Decimal(line[4].value)
    min_btc_quantity = decimal.Decimal(".00000001")
    crypto_quantity = decimal.Decimal(line[5].value).quantize(min_btc_quantity)
    fee_in_crypto = decimal.Decimal(line[7].value).quantize(min_btc_quantity)
    date = delorean.parse(line[13].value, dayfirst=False).datetime
    order_type = line[10].value
    if not order_type:
        return None  # Ignore if not market or limit.
    return _transaction_from_dict(
        market, operation, usd, price_in_fiat, crypto_quantity, fee_in_crypto, date
    )


class BybitParser(Format):
    EXCHANGE_HUMAN_READABLE_NAME = "Bybit"
    _EXCHANGE_ID_STR = _EXCHANGE_ID_STR

    @staticmethod
    def needs_binary():
        return True

    def parse(self):
        self._file.seek(0)
        workbook = openpyxl.load_workbook(self._file)
        sheet = workbook.active
        all_contents = list(sheet.rows)
        _raise_if_headers_bad(all_contents[0])
        contents = all_contents[1:]
        ans = []
        for row in contents:
            item = _tx_from_bybit_row(row)
            if item is not None:
                ans.append(item)
        self._reports = ans
        return ans

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


FORMAT_CLASSES.append(BybitParser)
