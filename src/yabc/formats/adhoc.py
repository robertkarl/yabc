"""
Adhoc transactions include mining, spending, and gifts.
"""
import csv
import datetime
import decimal

from yabc import transaction

field_names = ["Coin", "Amount","Timestamp","Type",]
VALID_TYPES = ["GIFT", "MINING"]

class AdhocTransactionGenerator:
    def __init__(self, csv_file):
        """

        :param csv_file: can be a list of rows, each containing a string, or an open file-like object.
        """
        self.reader = csv.DictReader(csv_file)

    def __next__(self):
        curr = next(self.reader)
        if curr['Type'] == "GIFT":
            op = transaction.Operation.GIFT
        else:
            op = transaction.Operation.NOOP
        trans_date = datetime.datetime.strptime(curr['Timestamp'], '%m/%d/%Y')
        trans = transaction.make_transaction(op, trans_date, quantity=decimal.Decimal(curr['Amount']),

