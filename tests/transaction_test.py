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
from yabc.formats import gemini
from yabc.transaction import Transaction
from yabc.transaction import make_transaction

BUY = Transaction.Operation.BUY
SELL = Transaction.Operation.SELL


class TransactionTest(unittest.TestCase):
    def setUp(self):
        self.sample_buy = make_transaction(Transaction.Operation.BUY, 1.0, 10.0, 100.0)

    def test_fees_no_proceeds(self):
        """ Test case where fees make a profit of 0.
        """
        date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
        pool = [
            transaction.Transaction(
                operation=BUY,
                quantity=0.5,
                source=None,
                usd_subtotal=990.0,
                date=date,
                asset_name="BTC",
                fees=10,
            )
        ]
        sale = transaction.Transaction(
            operation=SELL,
            quantity=0.5,
            source=None,
            usd_subtotal=1010.0,
            date=date,
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
        proceeds = 100
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
        ans_basis = 55.0
        sale_basis = 95.0
        ans_gain_or_loss = 40.0
        self.assertEqual(report.gain_or_loss, ans_gain_or_loss)

    def test_split_report_bad_input(self):
        """ Test where function split_report gets bad inputs and should throw / assert.
        """
        proceeds = 100
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

        trans = transaction.Transaction.FromCoinbaseJSON(coinbase_json_buy)

        self.assertEqual(trans.operation, BUY)
        self.assertEqual(trans.quantity, coinbase_json_buy["Amount"])
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 6, 27, 56, 373000))
        self.assertEqual(trans.usd_subtotal, 1.05)
        self.assertEqual(trans.source, "coinbase")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_coinbase_sell(self):
        """ Test loading a coinbase sell from json.
        """
        coinbase_json_sell = {
            "Transfer Total": 1.05,
            "Transfer Fee": 0.05,
            "Amount": -2,
            "Currency": "BTC",
            "Timestamp": "2015-2-5 06:27:56.373",
        }

        trans = transaction.Transaction.FromCoinbaseJSON(coinbase_json_sell)

        self.assertEqual(trans.operation, SELL)
        self.assertEqual(trans.quantity, math.fabs(coinbase_json_sell["Amount"]))
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 6, 27, 56, 373000))
        self.assertEqual(trans.usd_subtotal, 1.05)
        self.assertEqual(trans.source, "coinbase")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_gemini_buy(self):
        """ Test loading a gemini buy from json.
        """
        gemini_json_buy = {
            "Type": "Buy",
            "BTC Amount": 2,
            "USD Amount": 1,
            "USD Fee": "0.05",
            "Date": "2015-2-5",
            # TODO (robertkarl) fix this. Gemini currently ignores the time of day.
            # "Time": "06:27:56.373",
        }

        trans = gemini.FromGeminiJSON(gemini_json_buy)

        self.assertEqual(trans.operation, BUY)
        self.assertEqual(trans.quantity, 2)
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 0, 0))
        self.assertEqual(trans.usd_subtotal, 1.0)
        self.assertEqual(trans.fees, Decimal("0.05"))
        self.assertEqual(trans.source, "gemini")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_gemini_sell(self):
        """ Test loading a gemini sell from json.
        """
        gemini_json_sell = {
            "Type": "Sell",
            "BTC Amount": 2,
            "USD Amount": 1,
            "USD Fee": "0.05",
            "Date": "2015-2-5",
            # TODO (robertkarl) fix this. Gemini currently ignores the time of day.
            # "Time": "06:27:56.373",
        }

        trans = gemini.FromGeminiJSON(gemini_json_sell)

        self.assertEqual(trans.operation, SELL)
        self.assertEqual(trans.quantity, 2)
        self.assertEqual(trans.fees, Decimal("0.05"))
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 0, 0))
        self.assertEqual(trans.usd_subtotal, Decimal("1.0"))
        self.assertEqual(trans.source, "gemini")
        self.assertEqual(trans.asset_name, "BTC")

    def test_sql_create(self):
        """ Test modifying SQL db via ORM.
        """
        sell_json_gemini = {
            "Type": "Sell",
            "BTC Amount": 2,
            "USD Amount": 1,
            "USD Fee": Decimal("0.05"),
            "Date": "2015-2-5",
        }

        trans = gemini.FromGeminiJSON(sell_json_gemini)
        engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        session.add(trans)
        session.commit()


if __name__ == "__main__":
    unittest.main()
