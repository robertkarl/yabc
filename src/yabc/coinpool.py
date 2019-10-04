#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import enum
from collections import defaultdict
from typing import Sequence

from yabc import transaction


@enum.unique
class PoolMethod(enum.Enum):
    LIFO = 1
    FIFO = 2


class PoolDiff:
    """
    Operations to be applied to a CoinPool.

    Supports add and remove.
    """

    def __init__(self):
        self.to_add = []
        self.to_remove = []

    def add(self, symbol, coin):
        # type: (str, transaction.Transaction) -> None
        if not coin.symbol_received == symbol:
            raise RuntimeError("Cannot add to pool {}".format(symbol))
        self.to_add.append(coin)

    def remove(self, symbol, index):
        # type: (str, int) -> None
        """
        The coins up to and including this index will be REMOVED from the pool.
        """
        self.to_remove.append((symbol, index))


def _handle_add_lifo(pool, to_add: transaction.Transaction):
    """
    Simply put any new transaction, including splits, at the beginning.
    """
    pool.insert(0, to_add)


def _handle_add_fifo(pool, to_add: transaction.Transaction):
    """
    FIFO is defined by putting the BUY transactions at the end.
    For split coins, they need to be sold first.
    """
    if to_add.operation == transaction.Operation.SPLIT:
        pool.insert(0, to_add)
    else:
        assert to_add.operation in [
            transaction.Operation.BUY,
            transaction.Operation.MINING,
            transaction.Operation.GIFT_RECEIVED,
            transaction.Operation.TRADE_INPUT,
        ]
        pool.append(to_add)


class CoinPool:
    """
    Consider trading BTC, getting ETH, and paying the fee in ETH.

    - need to add ETH to the pool, less fees
    - need to remove BTC from the pool
        - potentially need to split a BTC coin
        - if so, need to add BTC to the pool

    Internal representation note: by convention, the coins at the START of the
    list will be sold first. This is for LIFO and FIFO.
    """

    def __init__(self, method):
        # type: (PoolMethod) -> None
        assert method in PoolMethod
        self._coins = defaultdict(list)
        self.method = method

    def known_symbols(self):
        return self._coins.keys()

    def get(self, coin_name):
        # type: (str) -> Sequence[transaction.Transaction]
        """
        Read-only access to the pool of transactions for a given symbol.

        Note that it's read-only by convention, and clients who modify the returned value are in for trouble.
        TODO: Consider returning a copy here (?)

        :return: A sequence of Transaction
        """
        return self._coins[coin_name]

    def apply(self, diff: PoolDiff):
        """
        Pop from the front of a list of txs, or add in the correct spot based on method.

        This mutates the object and isn't easy to undo.
        """
        for item in diff.to_add:
            coin_list = self._coins[item.asset_name]
            if self.method == PoolMethod.LIFO:
                _handle_add_lifo(coin_list, item)
            elif self.method == PoolMethod.FIFO:
                _handle_add_fifo(coin_list, item)
        for symbol, index in diff.to_remove:
            self._coins[symbol] = self._coins[symbol][index + 1 :]
