# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
"""
Imports binance exchange data into yabc's exchange-independent format.

yabc is not affiliated with the exchange or company Binance.

TODO: binance is the first supported format with coin/coin exchange defined.
      right now, the Transaction object is defined as an exchange of crypto for USD.
      Once we update Transaction to support this use case, we'll add more tests and
      take the binance format live.

"""
import decimal
import typing
from csv import DictReader

import delorean

from yabc import transaction
from yabc.formats import Format
from yabc.price_data import historical

HEADERS = "Date,Market,Type,Price,Amount,Total,Fee,Fee Coin".split(",")


def _fee_in_usd(date, coin, quantity: decimal.Decimal):
    return historical(date, coin) * quantity


_BINANCE_TYPE_MAP = {
    "SELL": transaction.Operation.SELL,
    "BUY": transaction.Operation.BUY,
}


def _transaction_from_binance_dict(
    date, market, type_str, price, amount, total, fee, feecoin
) -> typing.Sequence:
    fee = _fee_in_usd(date, feecoin, decimal.Decimal(fee))
    coin_sold = market[:3]
    coin_purchased = market[3:]
    usd_subtotal = decimal.Decimal(amount) * historical(date.date, coin_sold)
    return transaction.Transaction(
        _BINANCE_TYPE_MAP[type_str],
        asset_name=coin_sold,
        source="binance",
        date=date,
        quantity=decimal.Decimal(amount),
        usd_subtotal=usd_subtotal,
        fees=fee,
    )


class BinanceParser(Format):
    def parse(self):
        reader = DictReader(self._file)
        for line in reader:
            date = delorean.parse(line["Date"])
            market = line["Market"]
            type = line["Type"]
            price = line["Price"]
            amount = line["Amount"]
            total = line["Total"]
            fee = line["Fee"]
            fee_coin = line["Fee Coin"]
            self._reports.append(
                _transaction_from_binance_dict(
                    date, market, type, price, amount, total, fee, fee_coin
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
