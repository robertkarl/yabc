import datetime
import json
import math
import unittest
from decimal import Decimal
from yabc.server.sql_backend import SqlBackend

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import transaction
from yabc import user  # noqa

def make_transaction(kind, quantity, fees, subtotal):
    sample_date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
    return transaction.Transaction(
        date=sample_date,
        operation=kind,
        asset_name="BTC",
        fees=fees,
        quantity=quantity,
        usd_subtotal=subtotal,
    )

class SqlTest(unittest.TestCase):
    def setUp(self):
        self.db = SqlBackend(':memory:')
        self.db.create_tables()

    def test_modify_object(self):
        print('entering test')
        coinbase_json_buy = {
            "Transfer Total": "1.05",
            "Transfer Fee": "0.05",
            "Amount": 2,
            "Timestamp": "2015-2-5 06:27:56.373",
        }
        self.db.user_create('ralph-2')
        self.db.add_tx(1, json.dumps(coinbase_json_buy))
        self.db.tx_update(userid=1, txid=1, values={"quantity": 2})
        stuff = json.loads(self.db.tx_list(userid=1))
        self.assertEqual(stuff[0]['quantity'], '2')
        with SqlBackend("memory") as asdf:
            pass

if __name__ == "__main__":
    unittest.main()
