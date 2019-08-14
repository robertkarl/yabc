#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import decimal
import unittest

from yabc import transaction
from yabc.formats import gemini


class GeminiCsvTest(unittest.TestCase):
    def test_load_from_csv(self):
        txs = list(gemini.GeminiParser("./testdata/gemini/gemini.csv"))
        buy, sell = txs
        self.assertEqual(buy.date.date(), datetime.date(2015, 10, 16))
        self.assertEqual(sell.date.date(), datetime.date(2018, 1, 2))

        self.assertTrue(buy.operation == transaction.Operation.BUY)
        self.assertTrue(sell.operation == transaction.Operation.SELL)
        self.assertTrue(sell.fees == decimal.Decimal("1.22"))
        self.assertTrue(buy.fees == decimal.Decimal(".13"))
        self.assertTrue(sell.quantity == decimal.Decimal("0.03447186"))
        self.assertTrue(buy.quantity == decimal.Decimal("0.2092"))

        self.assertEqual(buy.source, "gemini")
        self.assertEqual(sell.source, "gemini")

        self.assertEqual(buy.usd_subtotal, decimal.Decimal("53.62"))
        self.assertEqual(sell.usd_subtotal, decimal.Decimal("489.45"))
