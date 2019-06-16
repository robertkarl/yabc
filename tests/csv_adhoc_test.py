"""
Test that we can parse data from various CSV sources.

"""
import datetime
import unittest
from decimal import Decimal

from yabc import transaction
from yabc.formats import adhoc


class CsvAdhocTest(unittest.TestCase):
    def test_load_gifts_mining(self):
        lists_per_row = [
            adhoc.field_names,
            ["BTC", "1.1", "2019/5/17", "Mining"],
            ["BTC", "0.1", "2019/5/18", "Gift"],
        ]
        csv_module_importable = [",".join(i) for i in lists_per_row]
        atg = adhoc.AdhocTransactionGenerator(csv_module_importable)
        l = list(atg)
        self.assertEqual(len(l), 2)
        mining = l[0]
        gift = l[1]
        self.assertEqual(mining.quantity, Decimal("1.1"))
        self.assertEqual(mining.operation, transaction.Operation.MINING)
        self.assertEqual(mining.date, datetime.datetime(2019, 5, 17))
        self.assertEqual(mining.asset_name, "BTC")

        self.assertEqual(gift.operation, transaction.Operation.GIFT)
        self.assertEqual(gift.date, datetime.datetime(2019, 5, 18))
        self.assertEqual(gift.quantity, Decimal("0.1"))
