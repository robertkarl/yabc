#  Copyright (c) 2019. Robert Karl. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import decimal
import unittest

from tests.transaction_utils import make_buy
from yabc import basis
from yabc import coinpool
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
        self.reports = self.bp.process()

    def test_coin_to_coin_pool_remnants(self):
        """
        The ETH/BTC trade above generates a TRADE_INPUT. Check its fields.

        Also check that the ETH is gone.
        """
        remaining_btc = self.bp.get_pool().get("BTC")[0]
        self.assertEqual(remaining_btc.quantity_received, 8)
        self.assertEqual(remaining_btc.date, datetime.datetime(2017, 1, 1))
        self.assertEqual(remaining_btc.symbol_received, "BTC")
        price = 1000 * decimal.Decimal("8.6")
        self.assertEqual(remaining_btc.quantity_traded, price)
        self.assertEqual(remaining_btc.symbol_traded, "USD")
        self.assertEqual(remaining_btc.fee_symbol, "USD")
        self.assertEqual(remaining_btc.fees, 0)
        self.assertEqual(len(self.bp.get_pool().get("ETH")), 0)

    def test_single_transaction(self):
        """
        A single coin/coin trade, following a buy. Check the results minus fees.
        """

        self.assertEqual(len(self.reports), 1)
        report = self.reports[0]
        daily_val = decimal.Decimal("1008.6")
        value_of_sell = 8 * daily_val
        fees = decimal.Decimal(".001") * daily_val
        computed_value = value_of_sell - fees
        self.assertEqual(report.proceeds, computed_value.quantize(1))
        pool = self.bp.get_pool()
        self.assertEqual(len(pool._coins.keys()), 2)
        self.assertEqual(len(pool.get("BTC")), 1)
