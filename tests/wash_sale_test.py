import datetime
import math
import unittest
from decimal import Decimal

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import transaction
from yabc import user  # noqa

import transaction_test
from yabc.costbasisreport import CostBasisReport


class WashSaleTest(unittest.TestCase):

    def setUp(self):
        self.buy = transaction.Transaction('BTC', datetime.datetime(2018, 1, 1), fees=0, operation='Buy', quantity=2, usd_subtotal=11000)
        self.wash_sale = transaction.Transaction('BTC', datetime.datetime(2018, 1, 30), quantity=1, operation='Sell', usd_subtotal=1000)
        self.long_term_cap_gains_sale = transaction.Transaction('BTC', datetime.datetime(2019, 1, 1), quantity=1, operation='Sell', usd_subtotal=1000)

    def test_fifo_wash_followed_by_long_term_gains(self):
        """
        Ensure that a wash sale followed by a sale a year later works as expected.

        :return:
        """
        trans = [self.buy, self.wash_sale, self.long_term_cap_gains_sale]
        wash_report, long_term_report = basis.process_all_fifo(trans)
        self.assertEqual(wash_report.adjustment_code, CostBasisReport.WASH_CODE)

