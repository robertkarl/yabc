import datetime
import math
import unittest

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import transaction
from yabc import basis
from yabc import user  # noqa


class TransactionTest(unittest.TestCase):
    def test_fees_no_proceeds(self):
        date = datetime.datetime(2015, 2, 5, 6, 27, 56, 373000)
        pool = [transaction.Transaction(
            operation='Buy', quantity=.5, source=None, usd_subtotal=990., date=date, asset_name="BTC", fees=10)]
        sale = transaction.Transaction(operation='Sell', quantity=.5, source=None, usd_subtotal=1010., date=date, asset_name="BTC", fees=10)
        # Cost basis: (purchase price + fees) / quantity = 500
        # Proceeds: (.5 / (1010 - 10)) = 500
        # This transaction should result in $0 of capital gains.
        result = basis.process_one(sale, pool)
        self.assertEqual(result["basis_reports"][0].gain_or_loss, 0)

