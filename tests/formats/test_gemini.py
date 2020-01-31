#  Copyright (c) 2019. Robert Karl. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import decimal
import unittest

from yabc import transaction
from yabc.formats import gemini


class GeminiXlsxTest(unittest.TestCase):
    def test_load_from_csv(self):
        txs = list(gemini.GeminiParser("./testdata/gemini/gemini.xlsx"))
        self.assertEqual(len(txs), 6)
        btc_buy = txs[0]
        btc_sell = txs[1]
        for zec_or_eth_tx in txs[2:6]:
            self.assertEqual(zec_or_eth_tx.quantity, 1)
            self.assertEqual(zec_or_eth_tx.source, "gemini")
        for eth_tx in txs[2:4]:
            self.assertEqual(eth_tx.asset_name, "ETH")
        for zec_tx in txs[4:6]:
            self.assertEqual(zec_tx.asset_name, "ZEC")

        self.assertEqual(
            btc_buy.date, datetime.datetime(2015, 10, 16, 6, 27, 56, 139998)
        )
        self.assertEqual(
            btc_sell.date, datetime.datetime(2015, 10, 16, 6, 27, 56, 139998)
        )

        self.assertTrue(btc_buy.operation == transaction.Operation.BUY)
        self.assertTrue(btc_sell.operation == transaction.Operation.SELL)
        self.assertEqual(btc_sell.fees, decimal.Decimal("1.22"))
        self.assertEqual(
            btc_buy.fees, decimal.Decimal(".13406059")
        )  # Yes, gemini files have this many digits on fees
        self.assertTrue(btc_sell.quantity == decimal.Decimal("0.03447186"))
        self.assertTrue(btc_buy.quantity == decimal.Decimal("0.2092"))

        self.assertEqual(btc_buy.source, "gemini")
        self.assertEqual(btc_sell.source, "gemini")

        self.assertEqual(btc_buy.usd_subtotal, decimal.Decimal("53.624236"))
        self.assertEqual(btc_sell.usd_subtotal, decimal.Decimal("489.45"))
