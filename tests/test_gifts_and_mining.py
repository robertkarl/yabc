"""
Test that we can parse and consume data from various non-trading txs in our own adhoc format.
"""
#  Copyright (c) 2019. Robert Karl. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import datetime
import unittest
from decimal import Decimal

from transaction_utils import make_transaction
from yabc import coinpool
from yabc import transaction
from yabc.basis import BasisProcessor
from yabc.transaction import Operation


class GiftsAndMiningTest(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime.datetime.now()
        self.one_day = datetime.timedelta(1)

    def test_gifts(self):
        purchase = make_transaction(Operation.BUY, 2, 0, 2000, date=self.start)
        gift_given = transaction.Transaction(
            operation=Operation.GIFT_SENT,
            quantity_received=0,
            symbol_received="USD",
            quantity_traded=1,
            symbol_traded="BTC",
            date=self.start + self.one_day,
        )
        # should trigger a short term gain of $1
        sale = make_transaction(
            Operation.SELL, 1, 0, 1001, date=self.start + self.one_day * 2
        )
        reports = BasisProcessor(
            coinpool.PoolMethod.FIFO, [purchase, gift_given, sale]
        ).process()
        self.assertEqual(len(reports), 1)
        sale_report = reports[0]
        self.assertEqual(sale_report.gain_or_loss, Decimal("1"))

    def test_mining(self):
        mined = transaction.Transaction(
            operation=Operation.MINING,
            quantity_received=1,
            symbol_received="BTC",
            quantity_traded=1000,
            symbol_traded="USD",
            date=self.start,
        )
        sold = make_transaction(
            Operation.SELL, 1, 0, 2000, date=self.start + self.one_day
        )
        reports = BasisProcessor(coinpool.PoolMethod.FIFO, [sold, mined]).process()
        self.assertEqual(reports[0].get_gain_or_loss(), 1000)
