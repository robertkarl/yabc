import unittest

from yabc import csv_to_json


class RunBasisTest(unittest.TestCase):
    def test_multi_asset_reports(self):
        csv_to_json.coinbase_to_dict("testdata/multi_asset_coinbase.csv")
        self.assertFalse(True)
