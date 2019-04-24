"""
Test that we can parse data from various CSV sources.

"""

import unittest

from yabc import csv_to_json


class CsvTest(unittest.TestCase):
    def test_load_coinbase_csv(self):
        """ Test wholesale load of coinbase data from CSV"""
        csv_to_json.coinbase_to_dict("testdata/synthetic_coinbase_csv.csv")

    def test_load_gemini_csv(self):
        """ Test wholesale load of gemini data from CSV"""
        csv_to_json.gemini_to_dict("testdata/synthetic_gemini_csv.csv")
