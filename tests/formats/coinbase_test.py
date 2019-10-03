"""
Simple check that we can parse data from our coinbase files.
"""
#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import glob
import unittest

from yabc import transaction
import yabc.formats
from yabc.formats import coinbase


class CoinbaseCsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filenames = glob.glob("testdata/coinbase/*.csv")

    def test_load_coinbase_csvs(self):
        """ Test loading coinbase data from CSV does not raise
        TODO: perform better checks here.
        """
        self.assertEqual(len(self.filenames), 4)
        for fname in self.filenames:
            with open(fname) as f:
                coinbase.from_coinbase(f)

    def test_loading_sample(self):
        fname = "testdata/coinbase/sample_coinbase.csv"
        parser = yabc.formats.coinbase.CoinbaseParser(fname)
        txs = [i for i in parser]
        self.assertEqual(len(txs), 13)
        buys = [i for i in txs if i.operation == transaction.Operation.BUY]
        sales = [i for i in txs if i.operation == transaction.Operation.SELL]
        self.assertEqual(len(buys), 12)
        self.assertEqual(len(sales), 1)
