#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import unittest

from transaction_utils import make_buy
from yabc import basis
from yabc import coinpool
from yabc import transaction


class CoinToCoinTest(unittest.TestCase):
    def setUp(self):
        self.buy_eth = make_buy(
            1000,
            fees=0,
            subtotal=250 * 1000,
            date=datetime.datetime(2017, 12, 31),
            symbol="ETH",
        )
        self.sell_eth_to_btc = transaction.Transaction(
            operation=transaction.Operation.SELL,
            quantity_received=1,
            symbol_received="BTC",
            quantity_traded=1000,
            symbol_traded="ETH",
            fees=".001",
            fee_symbol="BTC",
            date=datetime.datetime(2018, 1, 1),
        )
        self.bp = basis.BasisProcessor(
            coinpool.PoolMethod.FIFO, [self.buy_eth, self.sell_eth_to_btc]
        )

    def _test_single_transation(self):
        """
        A single coin/coin trade, following a buy. Check the results minus fees.

        TODO: This fails for a couple reasons. Fix and enable it.
            1. we can't add a coin/coin trade to a pool. We need to create TradeInputs and add them.
            2. Without a historical price data source, we can't build CostBasisReports for coin/coin trades accurately.
        """
        reports = self.bp.process()

        self.assertEqual(len(reports), 1)
        report = reports[0]  # type: transaction.Transaction
        pool = self.bp.pool  # type: coinpool.CoinPool
        self.assertEqual(len(pool._coins.keys()), 1)
        self.assertEqual(len(pool.get("BTC")), 1)
