# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
"""
Imports binance exchange data into yabc's exchange-independent format.

yabc is not affiliated with the exchange or company Binance.
"""
import datetime
import decimal
from typing import Sequence

import delorean
import openpyxl

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

_DATE_HEADER = "created at"
_SIZE_HEADER = "size"
_SIZE_UNITS_HEADER = "size unit"
_FEE_HEADER = "fee"
_UNITS_HEADER = "price/fee/total unit"
_HEADERS = [
    "portfolio",
    "trade id",
    "product",
    "side",
    _DATE_HEADER,
    _SIZE_HEADER,
    _SIZE_UNITS_HEADER,
    "price",
    "fee",
    "total",
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


def _transaction_from_binance_dict(
    date, market, operation, amount, total, fee, feecoin
):
    # type: (datetime.datetime, str, transaction.Operation, decimal.Decimal, decimal.Decimal, decimal.Decimal, str)-> Sequence

    # The following fields are accurate if the tx is a BUY and not coin/coin.
    bm = CoinbaseProMarket(market)
    symbol_traded = bm.first()
    symbol_received = bm.second()
    quantity_traded = amount
    quantity_received = total
    is_coin_to_coin = not transaction.is_fiat(
        symbol_received
    ) and not transaction.is_fiat(symbol_traded)
    if operation == transaction.Operation.BUY:
        if is_coin_to_coin:
            operation = transaction.Operation.SELL
        # Swap all of these, and the operation
        symbol_received, symbol_traded = (symbol_traded, symbol_received)
        quantity_traded, quantity_received = quantity_received, quantity_traded

    return transaction.Transaction(
        operation=operation,
        source=_BINANCE_EXCHANGE_ID_STR,
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
    date = delorean.parse(line[0].value, dayfirst=False).datetime
    market = line[1].value
    operation = _TYPE_MAP[line[2].value]
    amount = decimal.Decimal(line[4].value)
    total = decimal.Decimal(line[5].value)
    fee = decimal.Decimal(line[6].value)
    fee_coin = line[7].value
    return _transaction_from_binance_dict(
        date, market, operation, amount, total, fee, fee_coin
    )


def _read_binance_txs_from_file(f):
    ans = []
    f.seek(0)
    workbook = openpyxl.load_workbook(f)
    sheet = workbook.active
    all_contents = list(sheet.rows)
    _raise_if_headers_bad(all_contents[0])
    contents = all_contents[1:]
    for row in contents:
        item = _tx_from_binance_row(row)
        if item is not None:
            ans.append(item)
    return ans


class BinanceParser(Format):
    EXCHANGE_HUMAN_READABLE_NAME = "Binance"
    _EXCHANGE_ID_STR = _BINANCE_EXCHANGE_ID_STR

    @staticmethod
    def needs_binary():
        return True

    def parse(self):
        self._reports = _read_binance_txs_from_file(self._file)

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


FORMAT_CLASSES.append(BinanceParser)
