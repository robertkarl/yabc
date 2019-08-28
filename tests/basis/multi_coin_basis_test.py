#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import unittest
import datetime

import yabc.basis
from yabc import transaction
from yabc.basis import BasisProcessor
from yabc.server.yabc_api import run_basis
from yabc.transaction import Operation as Op


class CoinToCoinTradeBasisTest(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_date = datetime.date(2017,1,1)
        self.delta = datetime.timedelta(1)

    def test_multi_symbol_pool_fails(self):
        buy_one_btc = transaction.Transaction(Op.BUY, quantity_received=1, symbol_received="BTC", quantity_traded=1000, symbol_traded="USD", date=self.sample_date)
        buy_lots_of_bch = transaction.Transaction(Op.BUY, quantity_received=1000, symbol_received="BCH", quantity_traded=1000, symbol_traded="USD", date=self.sample_date + self.delta)
        sell_bch = transaction.Transaction(Op.SELL, quantity_received=500, symbol_received="USD", quantity_traded=1000, symbol_traded="BCH", date=self.sample_date + 2 * self.delta)
        txs = [buy_one_btc, buy_lots_of_bch, sell_bch]
        # This shouldn't work
        bp = BasisProcessor("FIFO", txs)
        self.assertRaises(bp.process())
