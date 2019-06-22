import unittest

from yabc.basis import process_all
from yabc.transaction import *


class LifoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime.datetime.now()
        self.one_day = datetime.timedelta(1)
        self.purchase = make_transaction(Operation.BUY, 2, 0, 2000, date=self.start)

    def test_zero_gains(self):
        sale1 = make_transaction(
            Operation.SELL, 1, 0, 1000, date=self.start + self.one_day
        )
        sale2 = make_transaction(
            Operation.SELL, 1, 0, 1000, date=self.start + self.one_day * 2
        )
        reports = process_all("LIFO",[self.purchase, sale1, sale2])
        self.assertEqual(len(reports), 2)
        for i in reports:
            self.assertEqual(i.gain_or_loss, 0)

    def test_zero_gains_with_sale_fees(self):
        sale1 = make_transaction(
            Operation.SELL, 1, 10, 1010, date=self.start + self.one_day
        )
        sale2 = make_transaction(
            Operation.SELL, 1, 10, 1010, date=self.start + self.one_day * 2
        )
        reports = process_all("LIFO",[self.purchase, sale1, sale2])
        self.assertEqual(len(reports), 2)
        for i in reports:
            self.assertEqual(i.gain_or_loss, 0)

    def test_zero_gains_with_buy_fees(self):
        purchase_with_fees = make_transaction(
            Operation.BUY, 2, 20, 2000, date=self.start
        )
        sale1 = make_transaction(
            Operation.SELL, 1, 0, 1010, date=self.start + self.one_day
        )
        sale2 = make_transaction(
            Operation.SELL, 1, 0, 1010, date=self.start + self.one_day * 2
        )
        reports = process_all("LIFO",[purchase_with_fees, sale1, sale2])
        self.assertEqual(len(reports), 2)
        for i in reports:
            self.assertEqual(i.gain_or_loss, 0)

    def test_lifo_simple_basis(self):
        purchase1 = make_transaction(
            Operation.BUY, 1, 0, subtotal=100, date=self.start
        )
        purchase2 = make_transaction(
            Operation.BUY, 1, 0, subtotal=200, date=self.start
        )
        sale = make_transaction(
            Operation.SELL, 1, 0, 1200, date=self.start + self.one_day
        )
        reports = process_all("LIFO",[purchase1, purchase2, sale])
        self.assertEqual(len(reports), 1)
        r = reports[0]
        self.assertEqual(r.gain_or_loss, 1000)

    def test_lifo_with_split(self):
        purchase1 = make_transaction(
            Operation.BUY, 2, 0, subtotal=200, date=self.start
        )
        sale = make_transaction(
            Operation.SELL, 1, 0, 1100, date=self.start + self.one_day
        )
        reports = process_all("LIFO",[purchase1, sale])
        self.assertEqual(len(reports), 1)
        r = reports[0]
        self.assertEqual(r.gain_or_loss, 1000)

