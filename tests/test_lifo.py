import datetime
import unittest

from transaction_utils import make_buy
from transaction_utils import make_transaction
from yabc import coinpool
from yabc.basis import BasisProcessor
from yabc.transaction import Operation


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

        reports = BasisProcessor(
            coinpool.PoolMethod.LIFO, [self.purchase, sale1, sale2]
        ).process()
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
        reports = BasisProcessor(
            coinpool.PoolMethod.LIFO, [self.purchase, sale1, sale2]
        ).process()
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
        reports = BasisProcessor(
            coinpool.PoolMethod.LIFO, [purchase_with_fees, sale1, sale2]
        ).process()
        self.assertEqual(len(reports), 2)
        for i in reports:
            self.assertEqual(i.gain_or_loss, 0)

    def test_lifo_simple_basis(self):
        purchase1 = make_transaction(Operation.BUY, 1, 0, subtotal=100, date=self.start)
        purchase2 = make_transaction(
            Operation.BUY, 1, 0, subtotal=200, date=self.start + self.one_day
        )
        sale = make_transaction(
            Operation.SELL, 1, 0, 1200, date=self.start + 2 * self.one_day
        )
        reports = BasisProcessor(
            coinpool.PoolMethod.LIFO, [purchase1, purchase2, sale]
        ).process()
        self.assertEqual(len(reports), 1)
        r = reports[0]
        self.assertEqual(r.gain_or_loss, 1000)

    def test_lifo_with_split(self):
        purchase1 = make_buy(quantity=2, fees=0, subtotal=200, date=self.start)
        sale = make_transaction(
            Operation.SELL, 1, 0, 1100, date=self.start + 2 * self.one_day
        )
        reports = BasisProcessor(coinpool.PoolMethod.LIFO, [purchase1, sale]).process()
        self.assertEqual(len(reports), 1)
        r = reports[0]
        self.assertEqual(r.gain_or_loss, 1000)
