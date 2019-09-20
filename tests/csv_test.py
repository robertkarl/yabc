"""
Test that we can parse data from various CSV sources.
"""
import datetime
import decimal
import glob
import os
import unittest

from yabc import transaction
from yabc.formats import adhoc
from yabc.formats import coinbase


class CsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filenames = glob.glob("testdata/*coinbase*.csv")

    def test_load_coinbase_csvs(self):
        """ Test wholesale load of coinbase data from CSV"""
        for fname in self.filenames:
            with open(fname) as f:
                coinbase.from_coinbase(f)

    def test_load_adhoc_csv(self):
        """ Test wholesale load of gemini data from CSV"""
        print(os.environ)
        with open("testdata/adhoc.csv") as f:
            stuff = list(adhoc.AdhocParser(f))
            rcvd, sent, mining, spending, sell = stuff
            sell = sell  # type: transaction.Transaction
            self.assertEqual(len(stuff), 5)
            self.assertEqual(rcvd.operation, transaction.Operation.GIFT_RECEIVED)
            self.assertEqual(sent.operation, transaction.Operation.GIFT_SENT)
            self.assertEqual(mining.operation, transaction.Operation.MINING)
            self.assertEqual(spending.operation, transaction.Operation.SPENDING)
            self.assertEqual(sell.operation, transaction.Operation.SELL)
            self.assertEqual(sell.symbol_traded, "BTC")
            self.assertEqual(sell.quantity_received, 10000)
            self.assertEqual(sell.symbol_received, "ETH")
            self.assertEqual(sell.quantity_traded, decimal.Decimal(".33"))
            self.assertEqual(sell.date, datetime.datetime(2018, 5, 1))  # May 1
            self.assertEqual(sell.fees, 10)
            self.assertEqual(sell.fee_symbol, "BTC")
