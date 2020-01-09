import datetime
import unittest

from yabc import basis
from yabc import coinpool
from yabc import ohlcprovider
from yabc import transaction
from yabc import user  # noqa
from yabc.transaction import Transaction

BUY = Transaction.Operation.BUY
SELL = Transaction.Operation.SELL


class TransactionTest(unittest.TestCase):
    def setUp(self):
        self.history = [
            transaction.Transaction(
                operation=transaction.Operation.BUY,
                quantity_traded=1000,
                symbol_traded="USD",
                quantity_received=1,
                symbol_received="BTC",
                date=datetime.datetime(2018, 5, 22),
            )
        ]
        self.history.append(
            transaction.Transaction(
                operation=transaction.Operation.SELL,
                symbol_received="IOTA",
                symbol_traded="BTC",
                quantity_received="10",
                quantity_traded=".1",
                date=datetime.date(2019, 4, 16),
            )
        )
    def test_sell_of_valueless_coin(self):
        bp = basis.BasisProcessor(method=coinpool.PoolMethod.FIFO, txs=self.history)
        reports = bp.process()
        flags = bp.flags()
        stuff = bp.get_pool()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].proceeds, 524)
        self.assertEqual(reports[0].long_term, False)
        self.assertEqual(reports[0].basis, 100)
        self.assertEqual(len(flags), 0)
        self.assertEqual(len(stuff.get('IOTA')), 1)
        self.assertEqual(len(stuff.get('BTC')), 1)

    def test_raise_on_no_data(self):
        tx = transaction.Transaction(
            operation=transaction.Operation.BUY,
            symbol_received="IOTANOTACOIN",
            symbol_traded="BTCNONEXISTENT",
            quantity_received="10",
            quantity_traded=".0001",
            date=datetime.date(2019, 4, 16),
        )
        with self.assertRaises(ohlcprovider.NoDataError):
            basis._fiat_value_for_trade(
                tx, ohlcprovider.OhlcProvider(), prefer_traded=True
            )

    def test_valueless_lookup(self):
        """
        Test valueless coin looks up value from bitcoin
        """
        tx = transaction.Transaction(
            operation=transaction.Operation.BUY,
            symbol_received="IOTA",
            symbol_traded="BTC",
            quantity_received="10",
            quantity_traded=".0001",
            date=datetime.date(2019, 4, 16),
        )
        ohlc = ohlcprovider.OhlcProvider()
        val1 = basis._fiat_value_for_trade(tx, ohlc, prefer_traded=True)
        val2 = basis._fiat_value_for_trade(tx, ohlc, prefer_traded=False)
        # Important thing is that both values are the same, and based on bitcoin's vaue on 4-16
        self.assertEqual(val1, val2)


if __name__ == "__main__":
    unittest.main()
