import unittest

from yabc.basis import process_all_fifo
from yabc.transaction import *


class GiftsTest(unittest.TestCase):
    def test_gifts(self):
        start = datetime.datetime.now()
        one_day = datetime.timedelta(1)
        purchase = make_transaction(Operation.BUY, 2, 0, 2000, date=start)
        gift_given = make_transaction(Operation.GIFT, 1, 0, 0, date=start + one_day)
        # should trigger a short term gain of $1
        sale = make_transaction(Operation.SELL, 1, 0, 1001, date=start + one_day * 2)
        reports = process_all_fifo([purchase, gift_given, sale])
        print(reports)
        self.assertEqual(len(reports), 1)
        sale_report = reports[0]
        self.assertEqual(sale_report.gain_or_loss, Decimal("1"))
