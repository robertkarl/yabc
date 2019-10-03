"""
Load and check for adhoc format.
"""
#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import datetime
import decimal
import unittest
from typing import Sequence

from yabc import transaction
from yabc.formats import adhoc


class AdhocCsvTest(unittest.TestCase):
    def test_load_adhoc_csv(self):
        """ Adhoc format load and check. """
        with open("testdata/adhoc/adhoc.csv") as f:
            stuff = list(
                adhoc.AdhocParser(f)
            )  # type: Sequence[transaction.Transaction]
            for tx in stuff:
                self.assertEqual(tx.source, "adhoc")
            gift_received = stuff[0]
            self.assertEqual(
                gift_received.operation, transaction.Operation.GIFT_RECEIVED
            )
            self.assertEqual(gift_received.date, datetime.datetime(2018, 3, 4))
            self.assertEqual(gift_received.quantity_received, 3)
            self.assertEqual(gift_received.symbol_received, "BTC")
            self.assertEqual(gift_received.quantity_traded, 750)
            self.assertEqual(gift_received.symbol_traded, "USD")

            gift_sent = stuff[1]
            self.assertEqual(gift_sent.date, datetime.datetime(2018, 3, 6, 19, 57))
            self.assertEqual(gift_sent.operation, transaction.Operation.GIFT_SENT)
            self.assertEqual(gift_sent.quantity_traded, 1)
            self.assertEqual(gift_sent.symbol_traded, "BTC")
            self.assertEqual(gift_sent.symbol_received, "USD")
            self.assertEqual(gift_sent.quantity_received, 0)

            mining = stuff[2]
            self.assertEqual(mining.operation, transaction.Operation.MINING)
            self.assertEqual(mining.fees, 0)
            self.assertEqual(mining.quantity_received, decimal.Decimal("0.25"))
            self.assertEqual(mining.symbol_received, "BTC")

            spending = stuff[3]
            self.assertEqual(spending.operation, transaction.Operation.SPENDING)
            self.assertEqual(spending.symbol_received, "USD")
            self.assertEqual(spending.symbol_traded, "BTC")
            self.assertEqual(spending.quantity_received, 1000)
            self.assertEqual(spending.quantity_traded, decimal.Decimal(".33"))
            self.assertEqual(spending.date, datetime.datetime(2018, 5, 1))
            self.assertEqual(spending.fees, 15)
            self.assertEqual(spending.fee_symbol, "USD")

            eth_rcvd = stuff[4]
            self.assertEqual(
                eth_rcvd.operation, transaction.Operation.GIFT_RECEIVED
            )
            self.assertEqual(eth_rcvd.date, datetime.datetime(2018, 5, 21))
            self.assertEqual(eth_rcvd.quantity_received, 10001)
            self.assertEqual(eth_rcvd.symbol_received, "ETH")

            sell = stuff[5]
            self.assertEqual(sell.operation, transaction.Operation.SELL)
            self.assertEqual(sell.date, datetime.datetime(2018, 5, 22))
            self.assertEqual(sell.symbol_received, "BTC")
            self.assertEqual(sell.quantity_received, decimal.Decimal(".33"))
            self.assertEqual(sell.symbol_traded, "ETH")
            self.assertEqual(sell.quantity_traded, 10000)
            self.assertEqual(sell.fees, decimal.Decimal(".001"))
            self.assertEqual(sell.fee_symbol, "BTC")

            buy = stuff[5]
            self.assertEqual(buy.operation, transaction.Operation.BUY)
            self.assertEqual(buy.quantity_received, 15)
            self.assertEqual(buy.symbol_received, "BTC")
            self.assertEqual(buy.quantity_traded, 12345)
            self.assertEqual(buy.symbol_traded, "USD")
            self.assertEqual(buy.fees, 10)
            self.assertEqual(buy.fee_symbol, "USD")
