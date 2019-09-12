#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import unittest

from yabc import transaction, coinpool
from yabc import basis


class CoinToCoinTest(unittest.TestCase):

    def setUp(self) -> None:
        self.buy_btc_with_eth = transaction.Transaction(operation=transaction.Operation.SELL, quantity_received=1,
                                              symbol_received="BTC", quantity_traded=1000, symbol_traded='ETH',
                                              fees=.001, fee_symbol='BTC', date=datetime.datetime(2018, 1, 1))
        self.bp = basis.BasisProcessor(coinpool.PoolMethod.FIFO, [self.buy_btc_with_eth])

    def test_single_transaction(self):
        """
        A single coin/coin trade
        """
        reports = self.bp.process()
        self.assertEqual(len(reports), 1)
        report = reports[0] # type: transaction.Transaction
        pool = self.bp.pool # type: coinpool.CoinPool
        self.assertEqual(len(pool._coins.keys()), 1)
        self.assertEqual(len(pool.get('BTC')), 1)


