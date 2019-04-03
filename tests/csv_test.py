"""
Test that we can parse data from various CSV sources.

"""

import datetime
import math
import unittest

from yabc import transaction
from  yabc import csv_to_json

class CsvTest(unittest.TestCase):
    def test_load_coinbase_csv(self):
        csv_to_json.coinbase_to_dict('testdata/synthetic_coinbase_csv.csv')
