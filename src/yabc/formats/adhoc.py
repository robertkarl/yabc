"""
Adhoc transactions include mining, spending, and gifts.
"""
import csv
import decimal
import enum

import delorean

from yabc import transaction

field_names = ["Coin", "Amount", "Timestamp", "Type"]


class AdhocTypes(enum.Enum):
    GIFT = transaction.Operation.GIFT.value
    MINING = transaction.Operation.MINING.value


class AdhocTransactionGenerator:
    def __init__(self, csv_file):
        """

        :param csv_file: can be a list of rows, each containing a string, or an open file-like object.
        """
        self.reader = csv.DictReader(csv_file)

    def __next__(self):
        curr = next(self.reader)
        if curr["Type"].upper() == AdhocTypes.GIFT.value.upper():
            op = transaction.Operation.GIFT
        elif curr["Type"].upper() == AdhocTypes.MINING.value.upper():
            op = transaction.Operation.MINING
        else:
            op = transaction.Operation.NOOP
        trans_date = delorean.parse(curr["Timestamp"]).datetime
        trans = transaction.make_transaction(
            op,
            quantity=decimal.Decimal(curr["Amount"]),
            fees=decimal.Decimal(0),
            subtotal=0,
            date=trans_date,
        )
        return trans

    def __iter__(self):
        return self
