"""
Test that we can parse data from various CSV sources.
"""
#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import glob
import unittest

from yabc.formats import coinbase


class CsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filenames = glob.glob("testdata/*coinbase*.csv")

    def test_load_coinbase_csvs(self):
        """ Test wholesale load of coinbase data from CSV"""
        for fname in self.filenames:
            with open(fname) as f:
                coinbase.from_coinbase(f)
