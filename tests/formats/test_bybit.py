import datetime
import decimal
import unittest
from typing import Sequence

from yabc import basis
from yabc import coinpool
from yabc import transaction
from yabc.formats import bybit


class BybitXLSXTest(unittest.TestCase):
    def setUp(self) -> None:
        binance_parser = bybit.BybitPNLParser(
            open("testdata/bybit/assets_history_account.xlsx", "br")
        )
        self.txs = list(binance_parser)  # type: Sequence[transaction.Transaction]
        bp = basis.BasisProcessor(coinpool.PoolMethod.FIFO, self.txs)
        self.reports = bp.process()

    def test_reports(self):
        self.assertEqual(len(self.reports), 2)
        r1 = self.reports[0]
        gain = 33
        self.assertEqual(r1.get_gain_or_loss(), gain)
        self.assertEqual(r1.basis, 0)
        self.assertEqual(r1.proceeds, gain)

        loss = 4
        r2 = self.reports[1]
        self.assertEqual(r2.get_gain_or_loss(), -4)
        self.assertEqual(r2.basis, loss)
        self.assertEqual(r2.proceeds, 0)

    def test_bybit_gain(self):
        self.assertEqual(len(self.txs), 2)
        gain = self.txs[0]
        self.assertEqual(gain.date.date(), datetime.date(2019, 3, 2))
        self.assertEqual(gain.operation, transaction.Operation.PERPETUAL_PNL)
        self.assertEqual(gain.symbol_traded, "BTCUSD")
        self.assertEqual(gain.quantity_received, decimal.Decimal("0.00839186"))
        self.assertEqual(gain.quantity_traded, 0)

    def test_bybit_loss(self):
        self.assertEqual(len(self.txs), 2)
        loss = self.txs[1]
        self.assertEqual(loss.date.date(), datetime.date(2019, 10, 10))
        self.assertEqual(loss.symbol_traded, "BTCUSD")
        self.assertEqual(loss.quantity_received, decimal.Decimal("-0.00047"))
        self.assertEqual(loss.quantity_traded, 0)
