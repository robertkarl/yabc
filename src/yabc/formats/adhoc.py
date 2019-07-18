"""
Adhoc transactions include mining, spending, and gifts.

TODO: For each supported input file type, like those from each exchange.
create a file like this one.
"""
import csv
import decimal

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

TRANSACTION_TYPE_HEADER = "Type"
SUBTOTAL_HEADER = "DollarValue"
field_names = ["Coin", "Amount", "Timestamp", TRANSACTION_TYPE_HEADER, SUBTOTAL_HEADER]


SUPPORTED = [
    transaction.Transaction.Operation.GIFT_RECEIVED,
    transaction.Transaction.Operation.GIFT_SENT,
    transaction.Transaction.Operation.MINING,
    transaction.Transaction.Operation.SPENDING,
]


class AdhocParser(Format):
    """
    Defines an input format for ad-hoc transactions like mining, spending, and gifts.

    This class translates CSV rows into transaction objects.
    """

    EXCHANGE_NAME = "adhoc transactions"

    def validate_headers(self, curr):
        for header_name in field_names:
            if header_name not in curr:
                raise RuntimeError(
                    "Incorrectly formatted adhoc file {}, missing header key {}".format(
                        self._file, header_name
                    )
                )

    def __init__(self, csv_file):
        """

        :param csv_file: can be a list of rows, each containing a string, or an
        open file-like object.
        """
        self._file = None
        assert not isinstance(csv_file, str)
        if isinstance(csv_file, (list, tuple)):
            self.validate_headers(csv_file[0])
        else:
            csv_file.seek(0)
            contents = []
            while True:
                line = csv_file.readline()
                if line:
                    contents.append(line)
                else:
                    break
            rawcsv = list(csv.reader(contents))
            if not rawcsv:
                raise RuntimeError("not enough rows in adhoc file {}".format(csv_file))
            fieldnames = rawcsv[0]
            self.validate_headers(fieldnames)
            csv_file.seek(0)
        self._file = csv_file
        self.reader = csv.DictReader(self._file)

    def __next__(self):
        curr = next(self.reader)
        if not curr:
            raise StopIteration
        for header_name in field_names:
            if header_name not in curr:
                raise RuntimeError(
                    "Incorrectly formatted adhoc file {}, missing header key {}".format(
                        self._file, header_name
                    )
                )

        op = None
        for t in SUPPORTED:
            if curr[TRANSACTION_TYPE_HEADER].upper() == t.value.upper():
                op = t
        if not op:
            op = transaction.Transaction.Operation.NOOP
        trans_date = delorean.parse(curr["Timestamp"], dayfirst=False).datetime

        usd_subtotal_str = (
            curr[SUBTOTAL_HEADER].strip("$").replace(",", "")
            if curr[SUBTOTAL_HEADER]
            else "0"
        )
        trans = transaction.make_transaction(
            op,
            quantity=decimal.Decimal(curr["Amount"]),
            fees=decimal.Decimal(0),
            subtotal=decimal.Decimal(
                usd_subtotal_str
            ),  # TODO: for mining we need to look up the value on the date mined.
            date=trans_date,
        )
        return trans

    def __iter__(self):
        return self


FORMAT_CLASSES.append(AdhocParser)
