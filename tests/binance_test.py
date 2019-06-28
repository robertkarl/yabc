"""
Copyright (c) Seattle Blockchain Solutions. All rights reserved.
Licensed under the MIT License. See LICENSE in the project root for license information.
"""
import datetime
import decimal
import unittest

from yabc.formats import binance
from yabc.transaction import Transaction


class BinanceCsvTest(unittest.TestCase):
    def test_load_gifts_mining(self):
        binance_parser = binance.BinanceParser(open("testdata/binance.csv"))
        reports = list(binance_parser)
        self.assertEqual(len(reports), 1)
        sell_to_eth = reports[0]
        self.assertEqual(sell_to_eth.operation, Transaction.Operation.SELL)
        self.assertEqual(sell_to_eth.usd_subtotal, 1000)
        self.assertEqual(sell_to_eth.date.date, datetime.date(2017, 1, 1))
        self.assertEqual(sell_to_eth.source, "binance")
        # For this transaction, the fee was paid as .01 ETH. Convert that to USD to get:
        eth_val_on_jan1 = 8  # TODO: update if we get better data for tests
        self.assertEqual(sell_to_eth.fees, decimal.Decimal(".01") * eth_val_on_jan1)
