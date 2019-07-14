"""
Copyright (c) Seattle Blockchain Solutions. All rights reserved.
Licensed under the MIT License. See LICENSE in the project root for license information.
"""
import datetime
import decimal
import unittest

from yabc.formats import binance, localbitcoins
from yabc.transaction import Transaction


class LocalbitcoinsCsvTest(unittest.TestCase):
    def test_load_from_csv(self):
        parser = localbitcoins.LocalBitcoinsParser(filename="testdata/localbitcoins-sample.csv")
        reports = list(parser)
        self.assertEqual(len(reports), 5)
        sell_to_eth = reports[0]
        self.assertEqual(sell_to_eth.operation, Transaction.Operation.SELL)
        self.assertEqual(sell_to_eth.usd_subtotal, 1000)
        self.assertEqual(sell_to_eth.date.date, datetime.date(2017, 1, 1))
        self.assertEqual(sell_to_eth.source, "binance")
        # For this transaction, the fee was paid as .01 ETH. Convert that to USD to get:
        eth_val_on_jan1 = 8  # TODO: update if we get better data for tests
        self.assertEqual(sell_to_eth.fees, decimal.Decimal(".01") * eth_val_on_jan1)
