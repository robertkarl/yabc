import datetime
import math
import unittest
from decimal import Decimal

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import transaction_utils
from yabc import Base
from yabc import basis
from yabc import coinpool
from yabc import transaction
from yabc import user  # noqa
from yabc.formats import coinbase
from yabc.transaction import Transaction

BUY = Transaction.Operation.BUY
SELL = Transaction.Operation.SELL


class TransactionTest(unittest.TestCase):
    def setUp(self):
        self.sample_buy_date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
        self.sample_buy = transaction_utils.make_buy(
            0.5, 10, 990, date=self.sample_buy_date
        )

    def test_fees_no_proceeds(self):
        """ Test case where fees make a profit of 0.
        """
        pool = coinpool.CoinPool(coinpool.PoolMethod.LIFO)
        diff = coinpool.PoolDiff()
        diff.add(self.sample_buy.symbol_received, self.sample_buy)
        pool.apply(diff)
        sale = transaction_utils.make_sale(
            quantity=0.5,
            subtotal=1010.0,
            date=self.sample_buy_date,
            symbol="BTC",
            fees=10,
        )
        # Cost basis: (purchase price + fees) / quantity = 500
        # Proceeds: (.5 / (1010 - 10)) = 500
        # This transaction should result in $0 of capital gains.
        reports, _, _ = basis._process_one(sale, pool)
        self.assertEqual(reports[0].gain_or_loss, 0)

    def test_split_report_no_gain(self):
        """ Test simple case with no profit or loss.
        """
        buy = transaction_utils.make_buy(1.0, fees=0, subtotal=100.0)
        sell = transaction_utils.make_transaction(SELL, 1.0, 0, 100.0)
        report = basis._split_report(buy, Decimal("0.5"), sell)
        self.assertEqual(report.gain_or_loss, 0)

    def test_split_report(self):
        """ Test split_report function.
        """
        buy = transaction_utils.make_transaction(BUY, 1.0, 10, 100.0)
        sell = transaction_utils.make_transaction(SELL, 1.0, 10, 200.0)
        report = basis._split_report(buy, Decimal("0.5"), sell)
        ans_gain_or_loss = 40.0
        self.assertEqual(report.gain_or_loss, ans_gain_or_loss)

    def test_split_report_bad_input(self):
        """ Test where function split_report gets bad inputs and should throw / assert.
        """
        purchase_quantity = 1.0
        buy = transaction_utils.make_transaction(BUY, purchase_quantity, 0, 100.0)
        sell = transaction_utils.make_transaction(SELL, 2.0, 0, 100.0)
        with self.assertRaises(AssertionError):
            basis._split_report(
                buy, purchase_quantity, sell
            )  # Should not split the basis coin, quantity matches

    def test_from_coinbase_buy(self):
        """ Test loading a coinbase tx from json.
        """
        coinbase_json_buy = {
            "Transfer Total": 1.05,
            "Transfer Fee": 0.05,
            "Amount": 2,
            "Currency": "BTC",
            "Timestamp": "2015-2-5 06:27:56.373",
        }

        trans = coinbase.FromCoinbaseJSON(coinbase_json_buy)

        self.assertEqual(trans.operation, BUY)
        self.assertEqual(trans.quantity, coinbase_json_buy["Amount"])
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 6, 27, 56, 373000))
        self.assertEqual(trans.usd_subtotal, 1.05)
        self.assertEqual(trans.source, "coinbase")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_coinbase_sell(self):
        """ Test loading a coinbase sell from json.
        TODO: Consider moving this to a Coinbase specific test.
        """
        coinbase_json_sell = {
            "Transfer Total": 1.05,
            "Transfer Fee": 0.05,
            "Amount": -2,
            "Currency": "BTC",
            "Timestamp": "2015-2-5 06:27:56.373",
        }

        trans = coinbase.FromCoinbaseJSON(coinbase_json_sell)

        self.assertEqual(trans.operation, SELL)
        self.assertEqual(trans.quantity, math.fabs(coinbase_json_sell["Amount"]))
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 6, 27, 56, 373000))
        self.assertEqual(trans.usd_subtotal, 1.05)
        self.assertEqual(trans.source, "coinbase")
        self.assertEqual(trans.asset_name, "BTC")

    def test_sql_create(self):
        """ Test modifying SQL db via ORM.
        """
        trans = self.sample_buy
        engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.add(trans)
        session.commit()

    def test_is_coin_to_coin(self):
        trans = transaction.Transaction(
            operation=transaction.Operation.SELL,
            quantity_received=1,
            symbol_received="BTC",
            quantity_traded=1000,
            symbol_traded="ETH",
        )
        self.assertEqual(trans.is_coin_to_coin(), True)
        self.assertEqual(self.sample_buy.is_coin_to_coin(), False)
        trans = transaction.Transaction(
            operation=transaction.Operation.BUY,
            quantity_received=1,
            symbol_received="BTC",
            quantity_traded=1000,
            symbol_traded="ETH",
        )
        self.assertEqual(trans.is_coin_to_coin(), True)
        mining = transaction.Transaction(
            operation=transaction.Operation.MINING,
            quantity_received=1,
            symbol_received="BTC",
            symbol_traded="USD",
            quantity_traded=10000,
        )

        self.assertEqual(mining.is_coin_to_coin(), False)


if __name__ == "__main__":
    unittest.main()
