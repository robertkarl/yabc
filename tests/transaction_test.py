import datetime
import math
import unittest

from yabc import transaction

class TransactionTest(unittest.TestCase):
    def test_from_coinbase_buy(self):
        coinbase_json_buy = {
            "Transfer Total": 1.05,
            "Transfer Fee": 0.05,
            "Amount": 2,
            # TODO(robertkarl): What does the coinbase format look like?
            "Timestamp": "2015-2-5 06:27:56.373",
        }

        trans = transaction.Transaction.FromCoinbaseJSON(coinbase_json_buy)

        self.assertEqual(trans.operation, "Buy")
        self.assertEqual(trans.btc_quantity, coinbase_json_buy["Amount"])
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 6, 27, 56, 373000))
        self.assertEqual(trans.usd_btc_price, 0.5)
        self.assertEqual(trans.source, "coinbase")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_coinbase_sell(self):
        coinbase_json_sell = {
            "Transfer Total": 1.05,
            "Transfer Fee": 0.05,
            "Amount": -2,
            "Timestamp": "2015-2-5 06:27:56.373",
        }

        trans = transaction.Transaction.FromCoinbaseJSON(coinbase_json_sell)

        self.assertEqual(trans.operation, "Sell")
        self.assertEqual(trans.btc_quantity, math.fabs(coinbase_json_sell["Amount"]))
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 6, 27, 56, 373000))
        self.assertEqual(trans.usd_btc_price, 0.5)
        self.assertEqual(trans.source, "coinbase")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_gemini_buy(self):
        gemini_json_buy = {
            "Type": "Buy",
            "BTC Amount": 2,
            "USD Amount": 1,
            "USD Fee": 0.05,
            "Date": "2015-2-5",
            # TODO (robertkarl) fix this. Gemini currently ignores the time of day.
            # "Time": "06:27:56.373",
        }

        trans = transaction.Transaction.FromGeminiJSON(gemini_json_buy)

        self.assertEqual(trans.operation, "Buy")
        self.assertEqual(trans.btc_quantity, 2)
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 0, 0))
        self.assertEqual(trans.usd_btc_price, 0.5)
        self.assertEqual(trans.source, "gemini")
        self.assertEqual(trans.asset_name, "BTC")

    def test_from_gemini_sell(self):
        gemini_json_sell = {
            "Type": "Sell",
            "BTC Amount": 2,
            "USD Amount": 1,
            "USD Fee": 0.05,
            "Date": "2015-2-5",
            # TODO (robertkarl) fix this. Gemini currently ignores the time of day.
            # "Time": "06:27:56.373",
        }

        trans = transaction.Transaction.FromGeminiJSON(gemini_json_sell)

        self.assertEqual(trans.operation, "Sell")
        self.assertEqual(trans.btc_quantity, 2)
        self.assertEqual(trans.date, datetime.datetime(2015, 2, 5, 0, 0))
        self.assertEqual(trans.usd_btc_price, 0.5)
        self.assertEqual(trans.source, "gemini")
        self.assertEqual(trans.asset_name, "BTC")


if __name__ == "__main__":
    unittest.main()
