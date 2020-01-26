"""
Simple check that we can parse data from our coinbase files.
"""
#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import unittest

import yabc
from yabc import transaction
from yabc.formats import coinbasepro


class CoinbaseProCsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filenames = ["testdata/coinbase-pro/fills.csv"]

    def test_load_coinbase_pro_csv(self):
        for fname in self.filenames:
            with open(fname) as f:
                coinbasepro.CoinbaseProParser(file=f)

    def test_loading_sample(self):
        fname = "testdata/coinbase/sample_coinbase.csv"
        parser = yabc.formats.coinbase.CoinbaseParser(fname)
        txs = [i for i in parser]
        self.assertEqual(len(txs), 13)
        buys = [i for i in txs if i.operation == transaction.Operation.BUY]
        sales = [i for i in txs if i.operation == transaction.Operation.SELL]
        self.assertEqual(len(buys), 12)
        self.assertEqual(len(sales), 1)
