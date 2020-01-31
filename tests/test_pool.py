#  Copyright (c) 2019. Robert Karl. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import unittest

from yabc import coinpool
from yabc import transaction


class PoolRemoveSymbolMatches(unittest.TestCase):
    def setUp(self) -> None:
        pool = coinpool.CoinPool(coinpool.PoolMethod.FIFO)
        diff = coinpool.PoolDiff()
        yesterday = datetime.datetime.now() - datetime.timedelta(1)
        diff.add(
            "BCH",
            transaction.Transaction(
                transaction.Operation.BUY,
                asset_name="BCH",
                date=yesterday,
                quantity=1,
                usd_subtotal=100,
            ),
        )
        diff.add(
            "BTC",
            transaction.Transaction(
                transaction.Operation.BUY, date=yesterday, quantity=1, usd_subtotal=1000
            ),
        )
        pool.apply(diff)
        self.pool = pool

    def test_multi_pool_remove_symbol_matches(self):
        diff = coinpool.PoolDiff()
        diff.remove("BCH", 0)
        self.pool.apply(diff)
        self.assertEqual(self.pool.get("BCH"), [])
        self.assertEqual(len(self.pool.get("BTC")), 1)
