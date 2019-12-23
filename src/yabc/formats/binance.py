# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
"""
Imports binance exchange data into yabc's exchange-independent format.

yabc is not affiliated with the exchange or company Binance.

TODO: binance is the first supported format with coin/coin exchange defined.
      Once we have historical price data, we can take this live.
"""
import datetime
import decimal
from csv import DictReader
from typing import Sequence

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

HEADERS = "Date,Market,Type,Price,Amount,Total,Fee,Fee Coin".split(",")

_BINANCE_TYPE_MAP = {
    "SELL": transaction.Operation.SELL,
    "BUY": transaction.Operation.BUY,
}

_BINANCE_EXCHANGE_ID_STR = "binance"


def _transaction_from_binance_dict(
    date, market, operation, amount, total, fee, feecoin
):
    # type: (datetime.datetime, str, transaction.Operation, decimal.Decimal, decimal.Decimal, decimal.Decimal, str)-> Sequence

    # The following fields are accurate if the tx is a BUY and not coin/coin.
    symbol_traded = market[:3]
    symbol_received = market[3:]
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


class BinanceParser(Format):
    EXCHANGE_HUMAN_READABLE_NAME = "Binance"
    _EXCHANGE_ID_STR = _BINANCE_EXCHANGE_ID_STR

    def parse(self):
        reader = DictReader(self._file)
        for line in reader:
            for key in HEADERS:
                if key not in line:
                    raise RuntimeError("Not a valid binance file.")
            date = delorean.parse(line["Date"]).datetime
            market = line["Market"]
            operation = _BINANCE_TYPE_MAP[line["Type"]]
            amount = decimal.Decimal(line["Amount"])
            total = decimal.Decimal(line["Total"])
            fee = decimal.Decimal(line["Fee"])
            fee_coin = line["Fee Coin"]
            self._reports.append(
                _transaction_from_binance_dict(
                    date, market, operation, amount, total, fee, fee_coin
                )
            )

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
