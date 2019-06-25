"""
Test that we can parse data from various CSV sources.
"""

import glob
import unittest

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
        gemini.gemini_to_dict("testdata/synthetic_gemini_csv.csv")

    def test_load_adhoc_csv(self):
        """ Test wholesale load of gemini data from CSV"""
        with open("testdata/adhoc.csv") as f:
            list(adhoc.AdhocParser(f))
