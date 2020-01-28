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

_HEADERS = (
    "Date(UTC)",
    "Market",
    "Type",
    "Price",
    "Amount",
    "Total",
    "Fee",
    "Fee Coin",
)

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
    "BTC",
    "DASH",
    "DGD",
    "DOCK",
    "DOGE",
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
    "MATIC",
    "MOD",
    "MTL",
    "NANO",
    "NEO",
    "ONT",
    "PPT",
    "TOMO",
    "TRX",
    "USDT",
    "VEN",
    "VET",
    "WAVES",
    "WTC",
    "XLM",
    "XMR",
    "XRP",
    "XTZ",
}


_BINANCE_TYPE_MAP = {
    "SELL": transaction.Operation.SELL,
    "BUY": transaction.Operation.BUY,
}

_BINANCE_EXCHANGE_ID_STR = "binance"


class BinanceMarket:
    """ Parse coin/coin market names from Binance cells. Slightly complicated
    by the fact that some of the symbols have 4 characters
    """

    def __init__(self, market):
        possible_lengths = [3, 4, 5]
        for curr_len in possible_lengths:
            if market[:curr_len] in _KNOWN_COINS:
                self._first = market[:curr_len]
                self._second = market[curr_len:]
                return
        raise RuntimeError("Could not parse transaction from market {}".format(market))

    def first(self):
        return self._first

    def second(self):
        return self._second


def _transaction_from_binance_dict(
    date, market, operation, amount, total, fee, feecoin
):
    # type: (datetime.datetime, str, transaction.Operation, decimal.Decimal, decimal.Decimal, decimal.Decimal, str)-> Sequence

    # The following fields are accurate if the tx is a BUY and not coin/coin.
    bm = BinanceMarket(market)
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
    for i, h in enumerate(_HEADERS):
        if not row[i].value == h:
            raise RuntimeError(
                "Not a valid Binance file, header {} found".format(row[i].value)
            )


def _tx_from_binance_row(line):
    date = delorean.parse(line[0].value, dayfirst=False).datetime
    market = line[1].value
    operation = _BINANCE_TYPE_MAP[line[2].value]
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
