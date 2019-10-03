#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import unittest

import tests.transaction_utils
from yabc import basis
from yabc.coinpool import PoolMethod


class SingleSaleTest(unittest.TestCase):
    """
    Check that just a sale (no previous buy for that tx) raises a flag and
    generates a short term CostBasisReport.
    """

    def test_single_sale(self):
        txs = [tests.transaction_utils.make_sale()]
        bp = basis.BasisProcessor(PoolMethod.LIFO, txs)
        reports = bp.process()
        self.assertEqual(len(reports), 1)
        report = reports[0]
        self.assertEqual(report.date_sold, txs[0].date)
        self.assertEqual(report.date_purchased, txs[0].date)
        self.assertEqual(report.basis, 0)
        self.assertEqual(report.proceeds, txs[0].quantity_received)
        self.assertEqual(len(bp.flags()), 1)
