import unittest

from yabc import basis, coinpool
from yabc.formats import coinbase


class RunBasisTest(unittest.TestCase):
    def test_multi_asset_reports(self):
        with open("testdata/multi_asset_coinbase.csv") as f:
            stuff = coinbase.from_coinbase(f)
            txs = [coinbase.FromCoinbaseJSON(i) for i in stuff]
            reports = basis.process_all(coinpool.PoolMethod.LIFO, txs)
            self.assertEqual(len(reports), 2)
            self.assertSetEqual(set([i.asset_name for i in reports]), {"BCH", "BTC"})
