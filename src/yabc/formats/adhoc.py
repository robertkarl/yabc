"""
Adhoc transactions include mining, spending, and gifts.

TODO: For each supported input file type, like those from each exchange.
create a file like this one.
"""
import csv
import decimal
import enum

import delorean

from yabc import transaction

TRANSACTION_TYPE_HEADER = "Type"
SUBTOTAL_HEADER = "DollarValue"
field_names = ["Coin", "Amount", "Timestamp", TRANSACTION_TYPE_HEADER, SUBTOTAL_HEADER]


SUPPORTED = \
    [transaction.Transaction.Operation.GIFT_RECEIVED,
    transaction.Transaction.Operation.GIFT_SENT,
    transaction.Transaction.Operation.MINING,
    transaction.Transaction.Operation.SPENDING,]


class AdhocTransactionGenerator:
    """
    Defines an input format for ad-hoc transactions like mining, spending, and gifts.

    This class translates CSV rows into transaction objects.
    """
    def __init__(self, csv_file):
        """

        :param csv_file: can be a list of rows, each containing a string, or an
        open file-like object.
        """
        self._csv_file = csv_file
        self.reader = csv.DictReader(csv_file)

    def __next__(self):
        curr = next(self.reader)
        op = None
        for t in SUPPORTED:
            if curr[TRANSACTION_TYPE_HEADER].upper() == t.value.upper():
                op = t
        if not op:
            op = transaction.Transaction.Operation.NOOP
        trans_date = delorean.parse(curr["Timestamp"], dayfirst=False).datetime

        usd_subtotal_str = curr[SUBTOTAL_HEADER].strip('$') if curr[SUBTOTAL_HEADER] else "0"
        trans = transaction.make_transaction(
            op,
            quantity=decimal.Decimal(curr["Amount"]),
            fees=decimal.Decimal(0),
            subtotal=decimal.Decimal(usd_subtotal_str), #TODO: for mining we need to look up the value on the date mined.
            date=trans_date,
        )
        return trans

    def __iter__(self):
        return self
