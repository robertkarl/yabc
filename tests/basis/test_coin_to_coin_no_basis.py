#  Copyright (c) 2019. Robert Karl. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import decimal
import unittest

from yabc import basis
from yabc import coinpool
from yabc import transaction


class TestCoinToCoinNoBasis(unittest.TestCase):
    def setUp(self) -> None:
        self.date = datetime.datetime(2018, 5, 22)
        self.tx1 = transaction.Transaction(
            transaction.Operation.SELL,
            date=self.date,
            symbol_received="BTC",
            symbol_traded="ETH",
            quantity_received=1,
            quantity_traded=1000,
        )

    def test_no_basis_still_looks_up_price(self):
        """
        The issue with self.tx1 is that there is no existing coin to sell, no ETH to trade away.

        We should still look up the value of the received asset.
        """
        bp = basis.BasisProcessor(coinpool.PoolMethod.FIFO, [self.tx1])
        reports = bp.process()
        one_btc_in_fiat = decimal.Decimal("8423")
        report = reports[0]
        self.assertEqual(report.proceeds, one_btc_in_fiat)
        self.assertEqual(report.adjustment, 0)
        self.assertEqual(report.date_purchased, self.tx1.date)
        self.assertEqual(report.date_sold, self.tx1.date)
