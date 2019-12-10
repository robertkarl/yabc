"""
Simple check that we can parse data from TaxTransactionReport files.
"""
#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import glob
import unittest

import yabc.formats
from yabc import transaction
from yabc.formats import coinbasettr


class CoinbaseTTRCsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filename = 'testdata/coinbase/TaxTransactionsReport.csv'

    def test_load_coinbasettr(self):
        """ Test that loading does not raise
        """
        with open(self.filename) as f:
            coinbasettr.CoinbaseTTRParser(csv_content=f)
        coinbasettr.CoinbaseTTRParser(filename=self.filename)

    def test_loading_sample(self):
        with open(self.filename) as f:
            parser = coinbasettr.CoinbaseTTRParser(f)
            txs = [i for i in parser]
            self.assertEqual(len(txs), 8)
            buys = [i for i in txs if i.operation == transaction.Operation.BUY]
            sales = [i for i in txs if i.operation == transaction.Operation.SELL]
            self.assertEqual(len(buys), 7)
            self.assertEqual(len(sales), 1)
