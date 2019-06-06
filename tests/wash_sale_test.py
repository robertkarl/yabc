import datetime
import decimal
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
        self.assertEqual(wash_report.get_adjustment(), -1 * wash_report.get_gain_or_loss())
        self.assertTrue(long_term_report._is_long_term())

    def test_profits_no_wash(self):
        """
        Wash sales are only triggered if you lose money.

        :return:
        """
        self.wash_sale.usd_subtotal = decimal.Decimal(20000)
        trans = [self.buy, self.wash_sale]
        short_term_report = basis.process_all_fifo(trans)[0]
        self.assertEqual(short_term_report.adjustment_code, None)
        self.assertEqual(short_term_report.get_adjustment(), 0)

    def test_simple_wash(self):
        """
        Wash sales are only triggered if you lose money.

        :return:
        """
        buy = transaction.Transaction('BTC', datetime.datetime(2018, 1, 1), fees=0, operation='Buy', quantity=21, usd_subtotal=21 * 11_000)

        # This is a loss of $200,000
        huge_wash_loss = transaction.Transaction('BTC', datetime.datetime(2018, 1, 30), quantity=20, operation='Sell', usd_subtotal=20000)

        # Sell a single coin later on, and generate the massive loss from before
        # In actuality a single coin was sold for a loss of $10,000.
        # But it triggers the wash sale loss from before to kick in.
        sell_the_rest = transaction.Transaction('BTC', datetime.datetime(2018, 4, 30), quantity=1, operation='Sell', usd_subtotal=1000)
        txs = [buy, huge_wash_loss, sell_the_rest]
        wash, huge_loss = basis.process_all_fifo(txs)
        self.assertEqual(wash.adjustment_code, CostBasisReport.WASH_CODE)
        self.assertEqual(wash.get_adjustment(), 200_000) # This loss is disallowed!
        self.assertEqual(huge_loss.adjustment_code, None)

        # Loss for this one should be the $10,000  loss on selling 1, as well as the $200,000 disallowed from before.
        self.assertEqual(huge_loss.get_gain_or_loss(), -210_000)

