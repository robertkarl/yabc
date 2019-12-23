"""
Load and check for adhoc format.
"""
#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import datetime
import decimal
import unittest
from typing import Sequence

from yabc import basis
from yabc import coinpool
from yabc import transaction
from yabc.formats import adhoc


class AdhocCsvTest(unittest.TestCase):
    def setUp(self):
        with open("testdata/adhoc/adhoc.csv") as f:
            self.txs = list(
                adhoc.AdhocParser(f)
            )  # type: Sequence[transaction.Transaction]

    def test_load_adhoc_csv(self):
        """ Adhoc format load and check. """
        for tx in self.txs:
            self.assertEqual(tx.source, adhoc.AdhocParser.exchange_id_str())
            self.assertEqual(tx.source, 'adhoc')
        gift_received = self.txs[0]
        self.assertEqual(gift_received.operation, transaction.Operation.GIFT_RECEIVED)
        self.assertEqual(gift_received.date, datetime.datetime(2018, 3, 4))
        self.assertEqual(gift_received.quantity_received, 3)
        self.assertEqual(gift_received.symbol_received, "BTC")
        self.assertEqual(gift_received.quantity_traded, 750)
        self.assertEqual(gift_received.symbol_traded, "USD")

        gift_sent = self.txs[1]
        self.assertEqual(gift_sent.date, datetime.datetime(2018, 3, 6, 19, 57))
        self.assertEqual(gift_sent.operation, transaction.Operation.GIFT_SENT)
        self.assertEqual(gift_sent.quantity_traded, 1)
        self.assertEqual(gift_sent.symbol_traded, "BTC")
        self.assertEqual(gift_sent.symbol_received, "USD")
        self.assertEqual(gift_sent.quantity_received, 0)

        mining = self.txs[2]
        self.assertEqual(mining.operation, transaction.Operation.MINING)
        self.assertEqual(mining.fees, 0)
        self.assertEqual(mining.quantity_received, decimal.Decimal("0.25"))
        self.assertEqual(mining.symbol_received, "BTC")

        spending = self.txs[3]
        self.assertEqual(spending.operation, transaction.Operation.SPENDING)
        self.assertEqual(spending.symbol_received, "USD")
        self.assertEqual(spending.symbol_traded, "BTC")
        self.assertEqual(spending.quantity_received, 1000)
        self.assertEqual(spending.quantity_traded, decimal.Decimal(".33"))
        self.assertEqual(spending.date, datetime.datetime(2018, 5, 1))
        self.assertEqual(spending.fees, 15)
        self.assertEqual(spending.fee_symbol, "USD")

        eth_rcvd = self.txs[4]
        self.assertEqual(eth_rcvd.operation, transaction.Operation.GIFT_RECEIVED)
        self.assertEqual(eth_rcvd.date, datetime.datetime(2018, 5, 21))
        self.assertEqual(eth_rcvd.quantity_received, 10001)
        self.assertEqual(eth_rcvd.symbol_received, "ETH")

        sell = self.txs[5]
        self.assertEqual(sell.operation, transaction.Operation.SELL)
        self.assertEqual(sell.date, datetime.datetime(2018, 5, 22))
        self.assertEqual(sell.symbol_received, "BTC")
        self.assertEqual(sell.quantity_received, decimal.Decimal(".33"))
        self.assertEqual(sell.symbol_traded, "ETH")
        self.assertEqual(sell.quantity_traded, 10000)
        self.assertEqual(sell.fees, decimal.Decimal(".001"))
        self.assertEqual(sell.fee_symbol, "BTC")

    def test_buy_tx(self):
        buy = self.txs[6]
        self.assertEqual(buy.operation, transaction.Operation.BUY)
        self.assertEqual(buy.quantity_received, 15)
        self.assertEqual(buy.symbol_received, "BTC")
        self.assertEqual(buy.quantity_traded, 12345)
        self.assertEqual(buy.symbol_traded, "USD")
        self.assertEqual(buy.fees, 10)
        self.assertEqual(buy.fee_symbol, "USD")

    def test_coin_to_coin_report(self):
        """
        Check that we look up the value of the coins received and use that for proceeds.
        """
        bp = basis.BasisProcessor(coinpool.PoolMethod.LIFO, self.txs)
        reports = bp.process()
        coin_to_coin_report = reports[-1]
        self.assertEqual(coin_to_coin_report.proceeds, 2780)
