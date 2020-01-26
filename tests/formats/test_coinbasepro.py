import datetime
import decimal
import unittest
from typing import Sequence

from yabc import transaction
from yabc.formats import coinbasepro


class CoinbaseProCsvTest(unittest.TestCase):
    def setUp(self) -> None:
        self.filenames = ["testdata/coinbase-pro/fills.csv"]
        txs = None
        for fname in self.filenames:
            with open(fname) as f:
                txs = list(
                    coinbasepro.CoinbaseProParser(file=f)
                )  # type: Sequence[transaction.Transaction]
        self.txs = txs

    def test_sell_to_usd(self):
        txs = self.txs
        self.assertIsNotNone(txs)
        sell = txs[2]
        self.assertEqual(sell.operation, transaction.Operation.SELL)
        self.assertEqual(sell.quantity_received, decimal.Decimal("1740.27689"))
        self.assertEqual(sell.symbol_received, "USD")

        self.assertEqual(sell.quantity_traded, abs(decimal.Decimal("0.2")))
        self.assertEqual(sell.symbol_traded, "BTC")

        self.assertEqual(sell.date.date(), datetime.date(2020, 1, 21))
        self.assertEqual(sell.fees, decimal.Decimal("8.74511"))
        self.assertEqual(sell.fee_symbol, "USD")

    def test_sell_eth_to_btc(self):
        txs = self.txs
        self.assertIsNotNone(txs)
        sell = txs[1]
        self.assertEqual(sell.operation, transaction.Operation.SELL)
        self.assertEqual(sell.quantity_received, decimal.Decimal("0.0098493498"))
        self.assertEqual(sell.symbol_received, "BTC")

        self.assertEqual(sell.quantity_traded, abs(decimal.Decimal("0.51395867")))
        self.assertEqual(sell.symbol_traded, "ETH")

        self.assertEqual(sell.date.date(), datetime.date(2020, 1, 24))
        self.assertEqual(sell.fees, decimal.Decimal("0.000049494219921"))
        self.assertEqual(sell.fee_symbol, "BTC")

    def test_load_coinbase_pro_csv(self):
        txs = self.txs
        self.assertIsNotNone(txs)
        buy_eth_with_btc = txs[0]
        self.assertEqual(buy_eth_with_btc.operation, transaction.Operation.SELL)
        self.assertEqual(
            buy_eth_with_btc.quantity_received, decimal.Decimal("0.51395867")
        )
        self.assertEqual(buy_eth_with_btc.symbol_received, "ETH")
        self.assertEqual(
            buy_eth_with_btc.quantity_traded, abs(decimal.Decimal("-0.0099999911"))
        )
        self.assertEqual(buy_eth_with_btc.symbol_traded, "BTC")
        self.assertEqual(buy_eth_with_btc.date.date(), datetime.date(2020, 1, 21))
        self.assertEqual(buy_eth_with_btc.fees, decimal.Decimal("0.000049751199256"))
        self.assertEqual(buy_eth_with_btc.fee_symbol, "BTC")
