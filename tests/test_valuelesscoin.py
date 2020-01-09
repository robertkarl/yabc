import datetime
import unittest

from yabc import basis
from yabc import ohlcprovider
from yabc import transaction
from yabc import user  # noqa
from yabc.transaction import Transaction

BUY = Transaction.Operation.BUY
SELL = Transaction.Operation.SELL


class TransactionTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fees_no_proceeds(self):
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
