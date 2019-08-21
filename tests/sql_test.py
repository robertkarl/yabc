import datetime
import json
import unittest

from yabc import transaction
from yabc import user  # noqa
from yabc.server.sql_backend import SqlBackend


def make_transaction(kind, quantity, fees, subtotal):
    sample_date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
    return transaction.Transaction(
        date=sample_date,
        operation=kind,
        asset_name="BTC",
        fees=fees,
        quantity_traded=quantity,
        quantity_received=subtotal,
    )


class SqlTest(unittest.TestCase):
    def setUp(self):
        self.db = SqlBackend("sqlite:///:memory:")
        self.db.create_tables()

    def test_modify_object(self):
        coinbase_json_buy = {
            "Transfer Total": "1.05",
            "Transfer Fee": "0.05",
            "Amount": 2,
            "Currency": "BTC",
            "Timestamp": "2015-2-5 06:27:56.373",
        }
        self.db.user_create("ralph-2")
        self.db.add_tx(1, json.dumps(coinbase_json_buy))
        self.db.tx_update(userid=1, txid=1, values={"quantity": 2})
        stuff = json.loads(self.db.tx_list(userid=1))
        self.assertEqual(stuff[0]["quantity"], "2")


if __name__ == "__main__":
    unittest.main()
