#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import datetime
import unittest

from yabc import transaction
from yabc.basis import BasisProcessor
from yabc.costbasisreport import CostBasisReport
from yabc.transaction import Operation as Op


class CoinToCoinTradeBasisTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_date = datetime.datetime(2017, 1, 1)
        self.delta = datetime.timedelta(1)

    def test_multi_symbol_pool_fails(self):
        buy_one_btc = transaction.Transaction(
            Op.BUY,
            quantity=1,
            asset_name="BTC",
            usd_subtotal=1000,
            date=self.sample_date,
        )
        buy_lots_of_bch = transaction.Transaction(
            Op.BUY,
            quantity=1000,
            asset_name="BCH",
            usd_subtotal=1000,
            date=self.sample_date + self.delta,
        )
        sell_bch = transaction.Transaction(
            Op.SELL,
            quantity=1000,
            asset_name="BCH",
            usd_subtotal=500,
            date=self.sample_date + 2 * self.delta,
        )
        txs = [buy_one_btc, buy_lots_of_bch, sell_bch]
        # This shouldn't work
        bp = BasisProcessor("FIFO", txs)
        result = bp.process()
        self.assertEqual(len(result), 1)
        bch_sell: CostBasisReport = result[0]
        self.assertEqual(bch_sell.asset_name, "BCH")
