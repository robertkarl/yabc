#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import unittest

from transaction_utils import make_sale
from yabc import basis
from yabc.coinpool import CoinPool, PoolMethod


class SingleSaleTest(unittest.TestCase):
    def setUp(self) -> None:
        pass
    def test_single_sale(self):
        txs = [make_sale()]
        bp = basis.BasisProcessor(PoolMethod.LIFO, txs)
        reports = bp.process()
        self.assertEqual(len(reports), 1)
        report = reports[0]
        self.assertEqual(report.date_sold, txs[0].date)
        self.assertEqual(report.date_purchased, txs[0].date)
        self.assertEqual(report.basis, 0)
        self.assertEqual(report.proceeds, txs[0].quantity_received)
        self.assertEqual(len(bp.flags()), 1)
