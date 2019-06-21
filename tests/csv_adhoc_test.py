"""
Test that we can parse data from various our own adhoc format.
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
            ["BTC", "1.1", "2019/5/6", "Mining"],
            ["BTC", "0.1", "2019/5/18", "GiftReceived"],
            ["BTC", "0.1", "2019/5/11", "GiftSent"],
        ]
        csv_module_importable = [",".join(i) for i in lists_per_row]
        atg = adhoc.AdhocTransactionGenerator(csv_module_importable)
        l = list(atg)
        self.assertEqual(len(l), 3)
        mining = l[0]
        gift = l[1]
        gift_sent = l[2]
        self.assertEqual(mining.quantity, Decimal("1.1"))
        self.assertEqual(mining.operation, transaction.Operation.MINING)
        self.assertEqual(mining.date, datetime.datetime(2019, 5, 6))
        self.assertEqual(mining.asset_name, "BTC")

        self.assertEqual(gift.operation, transaction.Operation.GIFT_RECEIVED)
        self.assertEqual(gift.date, datetime.datetime(2019, 5, 18))
        self.assertEqual(gift.quantity, Decimal("0.1"))

        self.assertEqual(gift_sent.operation, transaction.Operation.GIFT_SENT)
        self.assertEqual(gift_sent.date, datetime.datetime(2019, 5, 11))
        self.assertEqual(gift_sent.quantity, Decimal("0.1"))
