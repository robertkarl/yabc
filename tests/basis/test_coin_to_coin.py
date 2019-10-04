#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import decimal
import unittest

from tests.transaction_utils import make_buy
from yabc import basis
from yabc import coinpool
from yabc import costbasisreport
from yabc import transaction


class CoinToCoinTest(unittest.TestCase):
    def setUp(self):
        self.buy_eth = make_buy(
            1000,
            fees=0,
            subtotal=9 * 1000,
            date=datetime.datetime(2017, 1, 1),
            symbol="ETH",
        )
        self.sell_eth_to_btc = transaction.Transaction(
            operation=transaction.Operation.SELL,
            quantity_received=8,
            symbol_received="BTC",
            quantity_traded=1000,
            symbol_traded="ETH",
            fees=".001",
            fee_symbol="BTC",
            date=datetime.datetime(2017, 1, 1),
        )
        self.bp = basis.BasisProcessor(
            coinpool.PoolMethod.FIFO, [self.buy_eth, self.sell_eth_to_btc]
        )

    def test_single_transation(self):
        """
        A single coin/coin trade, following a buy. Check the results minus fees.

        TODO: This fails for a couple reasons. Fix and enable it.
            1. we can't add a coin/coin trade to a pool. We need to create TradeInputs and add them.
            2. Without a historical price data source, we can't build CostBasisReports for coin/coin trades accurately.
        """
        reports = self.bp.process()

        self.assertEqual(len(reports), 1)
        report = reports[0]  # type: costbasisreport.CostBasisReport
        daily_val = decimal.Decimal("1008.6")
        value_of_sell = 8 * daily_val
        fees = decimal.Decimal(".001") * daily_val
        computed_value = value_of_sell - fees
        self.assertEqual(report.proceeds, computed_value.quantize(1))
        pool = self.bp.get_pool()
        self.assertEqual(len(pool._coins.keys()), 2)
        self.assertEqual(len(pool.get("BTC")), 1)
