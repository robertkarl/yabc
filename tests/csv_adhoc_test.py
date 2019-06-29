"""
Test that we can parse and consume data from various non-trading txs in our own adhoc format.
"""
import datetime
import unittest
from decimal import Decimal

from yabc import transaction
from yabc.basis import process_all
from yabc.formats import adhoc
from yabc.transaction import Operation
from yabc.transaction import make_transaction


class CsvAdhocTest(unittest.TestCase):
    def test_load_gifts_mining(self):
        lists_per_row = [
            adhoc.field_names,
            ["BTC", "1.1", "2019/5/6", "Mining"],
            ["BTC", "0.1", "2019/5/18", "GiftReceived"],
            ["BTC", "0.1", "2019/5/11", "GiftSent"],
        ]
        csv_module_importable = [",".join(i) for i in lists_per_row]
        atg = adhoc.AdhocParser(csv_module_importable)
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

    def setUp(self) -> None:
        self.start = datetime.datetime.now()
        self.one_day = datetime.timedelta(1)

    def test_gifts(self):
        purchase = make_transaction(Operation.BUY, 2, 0, 2000, date=self.start)
        gift_given = make_transaction(
            Operation.GIFT_SENT, 1, 0, 0, date=self.start + self.one_day
        )
        # should trigger a short term gain of $1
        sale = make_transaction(
            Operation.SELL, 1, 0, 1001, date=self.start + self.one_day * 2
        )
        reports = process_all("FIFO", [purchase, gift_given, sale])
        print(reports)
        self.assertEqual(len(reports), 1)
        sale_report = reports[0]
        self.assertEqual(sale_report.gain_or_loss, Decimal("1"))

    def test_mining(self):
        mined = make_transaction(Operation.MINING, 1, 0, 1000, date=self.start)
        sold = make_transaction(
            Operation.SELL, 1, 0, 2000, date=self.start + self.one_day
        )
        reports = process_all("FIFO", [sold, mined])
        self.assertEqual(reports[0].get_gain_or_loss(), 1000)
