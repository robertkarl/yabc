"""
Test that we can parse data from various CSV sources.
"""

import glob
import os
import unittest

from yabc import transaction
from yabc.formats import adhoc
from yabc.formats import coinbase
from yabc.formats import gemini


class CsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filenames = glob.glob("testdata/*coinbase*.csv")

    def test_load_coinbase_csvs(self):
        """ Test wholesale load of coinbase data from CSV"""
        for fname in self.filenames:
            with open(fname) as f:
                coinbase.from_coinbase(f)

    def test_load_gemini_csv(self):
        """ Test wholesale load of gemini data from CSV"""
        gemini.gemini_to_dict("testdata/gemini/synthetic_gemini_csv.csv")

    def test_load_adhoc_csv(self):
        """ Test wholesale load of gemini data from CSV"""
        print(os.environ)
        with open("testdata/adhoc.csv") as f:
            stuff = list(adhoc.AdhocParser(f))
            rcvd, sent, mining, spending = stuff
            self.assertEqual(len(stuff), 4)
            self.assertEqual(rcvd.operation, transaction.Operation.GIFT_RECEIVED)
            self.assertEqual(sent.operation, transaction.Operation.GIFT_SENT)
            self.assertEqual(mining.operation, transaction.Operation.MINING)
            self.assertEqual(spending.operation, transaction.Operation.SPENDING)
