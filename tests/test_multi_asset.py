#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import datetime
import unittest

import transaction_utils
from yabc import basis
from yabc import coinpool
from yabc.transaction import Operation

TEN_K = 10000


class MultiAssetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime.datetime.now()
        self.one_day = datetime.timedelta(1)
        self.purchase_bch = transaction_utils.make_buy(
            quantity=1,
            fees=0,
            subtotal=100,
            date=self.start - 2 * self.one_day,
            symbol="BCH",
        )
        self.purchase_btc = transaction_utils.make_transaction(
            Operation.BUY, 1, 0, TEN_K, date=self.start - self.one_day
        )

    def test_sell_matches_symbol(self):
        """
        Sort of an integration test (because it several classes underneath the process_all api)

        Make sure that when we sell BTC, we match with a previous BTC buy (and not BCH or something else)
        :return:
        """
        sell_btc_no_profit = transaction_utils.make_transaction(
            Operation.SELL, 1, 0, TEN_K, date=self.start + self.one_day
        )
        # Note that they don't need to be in order.
        processor = basis.BasisProcessor(
            coinpool.PoolMethod.FIFO,
            [self.purchase_bch, self.purchase_btc, sell_btc_no_profit],
        )
        reports = processor.process()
        self.assertEqual(len(reports), 1)
        report = reports[0]
        self.assertEqual(report.asset_name, "BTC")
        self.assertEqual(report.get_gain_or_loss(), 0)
        self.assertEqual(report.proceeds, TEN_K)
        self.assertEqual(processor.pool.get("BTC"), [])
        self.assertEqual(len(processor.pool.get("BCH")), 1)
