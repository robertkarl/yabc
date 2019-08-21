#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import unittest
import yabc.basis
from yabc import transaction
from yabc.transaction import make_transaction


class CoinToCoinTradeBasisTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_simple_coin_to_coin(self):
        buy_one_btc = transaction.Transaction(transaction.Transaction.Operation.BUY, quantity_received=1, symbol_received="BTC", quantity_traded=1000, symbol_traded="USD")
        trade_for_eth = transaction.Transaction(transaction.Transaction.Operation.SELL, quantity_received=150, symbol_received="ETH", quantity_traded=1, symbol_traded="BTC")
        pool = [
            buy_one_btc,
        ]
        result = yabc.basis.process_one(trade_for_eth, pool)
        reports = result['basis_reports']
        remove = result['remove_index']
        add_list = result['add']
        self.assertEqual(len(reports), 1)
        self.assertEqual(remove, 0)
        self.assertEqual(len(add_list), 1)
        self.assertEqual(add_list[0].operation, transaction.Operation.TRADE_INPUT)

