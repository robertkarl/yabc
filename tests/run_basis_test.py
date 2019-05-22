import unittest

from yabc import basis
from yabc import csv_to_json
from yabc.transaction import Transaction


class RunBasisTest(unittest.TestCase):
    def test_multi_asset_reports(self):
        stuff = csv_to_json.coinbase_to_dict("testdata/multi_asset_coinbase.csv")
        txs = [Transaction.FromCoinbaseJSON(i) for i in stuff]
        reports = basis.process_all_fifo(txs)
        self.assertEqual(len(reports), 2)
        self.assertSetEqual(set([i.asset_name for i in reports]), {"BCH", "BTC"})
