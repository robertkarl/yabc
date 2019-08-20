import datetime
import math
import unittest
from decimal import Decimal

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import transaction
from yabc import user  # noqa
from yabc.formats import coinbase
from yabc.transaction import Transaction, Market
from yabc.transaction import make_transaction

BUY = Transaction.Operation.BUY
SELL = Transaction.Operation.SELL


class TransactionTest(unittest.TestCase):
    def setUp(self):
        self.sample_buy_date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
        self.sample_buy = transaction.Transaction(
            operation=BUY,
            market=Market.BTCUSD,
            first_quantity=0.5,
            source=None,
            second_quantity=990.0,
            date=self.sample_buy_date,
            fees=10,
        )

    def test_fees_no_proceeds(self):
        """ Test case where fees make a profit of 0.
        """
        pool = [self.sample_buy]
        sale = transaction.Transaction(
            operation=SELL,
            first_quantity=0.5,
            source=None,
            second_quantity=1010.0,
            date=self.sample_buy_date,
            asset_name="BTC",
            fees=10,
        )
        # Cost basis: (purchase price + fees) / quantity = 500
        # Proceeds: (.5 / (1010 - 10)) = 500
        # This transaction should result in $0 of capital gains.
        result = basis.process_one(sale, pool)
        self.assertEqual(result["basis_reports"][0].gain_or_loss, 0)

    def test_split_report_no_gain(self):
        """ Test simple case with no profit or loss.
        """
        buy = make_transaction(BUY, 1.0, 0, 100.0)
        sell = make_transaction(SELL, 1.0, 0, 100.0)
        report = basis.split_report(buy, Decimal("0.5"), sell)
        self.assertEqual(report.gain_or_loss, 0)

    def test_split_report(self):
        """ Test split_report function.
        """
        buy = make_transaction(BUY, 1.0, 10, 100.0)
        sell = make_transaction(SELL, 1.0, 10, 200.0)
        report = basis.split_report(buy, Decimal("0.5"), sell)
        ans_gain_or_loss = 40.0
        self.assertEqual(report.gain_or_loss, ans_gain_or_loss)

    def test_split_report_bad_input(self):
        """ Test where function split_report gets bad inputs and should throw / assert.
        """
        purchase_quantity = 1.0
        buy = make_transaction(BUY, purchase_quantity, 0, 100.0)
        sell = make_transaction(SELL, 2.0, 0, 100.0)
        with self.assertRaises(AssertionError):
            basis.split_report(
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

        trans = coinbase.transaction_from_coinbase_json(coinbase_json_buy)

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

        trans = coinbase.transaction_from_coinbase_json(coinbase_json_sell)

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
        engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.add(trans)
        session.commit()


if __name__ == "__main__":
    unittest.main()
