"""
Copyright (c) Seattle Blockchain Solutions. All rights reserved.
Licensed under the MIT License. See LICENSE in the project root for license information.
"""
import datetime
import decimal
import unittest

from yabc.formats import localbitcoins
from yabc.transaction import Operation


class LocalbitcoinsCsvTest(unittest.TestCase):
    def test_load_from_csv(self):
        parser = localbitcoins.LocalBitcoinsParser(
            filename="testdata/localbitcoins/localbitcoins.csv"
        )
        reports = list(parser)
        self.assertEqual(len(reports), 3)
        buy_tx = reports[0]
        self.assertEqual(buy_tx.asset_name, "BTC")
        self.assertEqual(buy_tx.fees, 0)
        self.assertEqual(buy_tx.quantity, decimal.Decimal("1.0"))
        self.assertEqual(buy_tx.operation, Operation.BUY)
        self.assertEqual(buy_tx.date.date(), datetime.date(2017, 1, 2))

        sell = reports[1]
        self.assertEqual(sell.asset_name, "BTC")
        self.assertEqual(sell.fees, 0)
        self.assertEqual(sell.quantity, decimal.Decimal("0.03194888"))
        self.assertEqual(sell.operation, Operation.SELL)
        self.assertEqual(sell.date.date(), datetime.date(2017, 1, 11))
        parser.cleanup()
