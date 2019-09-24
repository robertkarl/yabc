import unittest

from transaction_utils import make_transaction
from yabc import coinpool
from yabc.basis import BasisProcessor
from yabc.transaction import *


class FifoTest(unittest.TestCase):
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
            coinpool.PoolMethod.FIFO, [self.purchase, sale1, sale2]
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
            coinpool.PoolMethod.FIFO, [self.purchase, sale1, sale2]
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
            coinpool.PoolMethod.FIFO, [purchase_with_fees, sale1, sale2]
        ).process()
        self.assertEqual(len(reports), 2)
        for i in reports:
            self.assertEqual(i.gain_or_loss, 0)
