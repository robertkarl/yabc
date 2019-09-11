"""
Copyright (c) Seattle Blockchain Solutions. All rights reserved.
Licensed under the MIT License. See LICENSE in the project root for license information.
"""
import datetime
import decimal
import unittest

from yabc import transaction
from yabc.formats import binance
from yabc.transaction import Transaction


class BinanceCsvTest(unittest.TestCase):
    def setUp(self) -> None:
        binance_parser = binance.BinanceParser(open("testdata/binance/binance.csv"))
        reports = list(binance_parser)
        self.assertEqual(len(reports), 4)
        self.sell_to_eth = reports[0]  # type: transaction.Transaction
        self.buy_btc_with_eth = reports[1]  # type: transaction.Transaction
        self.buy_btc_with_cash = reports[2]  # type: transaction.Transaction
        self.sell_btc = reports[3]  # type: transaction.Transaction

    def test_binance_sell(self):
        sell_to_eth = self.sell_to_eth
        self.assertEqual(sell_to_eth.operation, Transaction.Operation.SELL)
        # A SELL in the BTCETH market means trading away BTC and receiving ETH

        self.assertEqual(sell_to_eth.symbol_received, "ETH")
        self.assertEqual(sell_to_eth.quantity_received, 125)

        self.assertEqual(sell_to_eth.symbol_traded, "BTC")
        self.assertEqual(sell_to_eth.quantity_traded, 1)
        self.assertEqual(sell_to_eth.date.date, datetime.date(2017, 1, 1))
        self.assertEqual(sell_to_eth.source, "binance")

        # For this transaction, the fee was paid as .01 ETH. Convert that to USD to get:
        eth_val_on_jan1 = 8  # TODO: update if we get better data for tests
        self.assertEqual(sell_to_eth.fees, decimal.Decimal(".01"))
        self.assertEqual(sell_to_eth.fee_symbol, "ETH")

    def test_binance_buy(self):
        buy_btc = self.buy_btc_with_eth
        self.assertEqual(buy_btc.operation, transaction.Operation.SELL)
        self.assertEqual(buy_btc.symbol_received, "BTC")
        self.assertEqual(buy_btc.symbol_traded, "ETH")
        self.assertEqual(buy_btc.quantity_received, 1)
        self.assertEqual(buy_btc.quantity_traded, 125)

    def test_buy_btc_with_usd(self):
        buy = self.buy_btc_with_cash
        self.assertEqual(buy.operation, transaction.Operation.BUY)
        self.assertEqual(buy.quantity_received, 1)
        self.assertEqual(buy.symbol_received, "BTC")
        self.assertEqual(buy.quantity_traded, 10025)
        self.assertEqual(buy.symbol_traded, "USD")
        self.assertEqual(buy.fees, decimal.Decimal(".01"))

    def test_vanilla_sell_btc(self):
        sell = self.sell_btc
        self.assertEqual(sell.operation, transaction.Operation.SELL)
        self.assertEqual(sell.quantity_received, 10030)
        self.assertEqual(sell.symbol_received, "USD")
        self.assertEqual(sell.quantity_traded, 1)
        self.assertEqual(sell.symbol_traded, "BTC")
        self.assertEqual(sell.fees, decimal.Decimal(".01"))
