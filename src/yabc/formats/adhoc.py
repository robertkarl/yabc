"""
Adhoc transactions include mining, spending, and gifts.
"""
import csv
import decimal

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

TRANSACTION_TYPE_HEADER = "Type"
SUBTOTAL_HEADER = "DollarValue"
RECEIVED_CURRENCY = "ReceivedCurrency"
RECEIVED_AMOUNT = "ReceivedAmount"
field_names = ["Coin", "Amount", "Timestamp", TRANSACTION_TYPE_HEADER, SUBTOTAL_HEADER, RECEIVED_CURRENCY, RECEIVED_AMOUNT]


SUPPORTED = [
    transaction.Transaction.Operation.GIFT_RECEIVED,
    transaction.Transaction.Operation.GIFT_SENT,
    transaction.Transaction.Operation.MINING,
    transaction.Transaction.Operation.SPENDING,
    transaction.Transaction.Operation.SELL,
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
        usd_amount = decimal.Decimal(usd_subtotal_str)
        crypto_amount = decimal.Decimal(curr["Amount"])
        if (
            op == transaction.Operation.GIFT_RECEIVED
            or op == transaction.Operation.MINING
        ):
            trans = transaction.Transaction(
                operation=op,
                quantity_received=crypto_amount,
                symbol_received=curr["Coin"],
                fees=decimal.Decimal(0),
                symbol_traded="USD",
                quantity_traded=usd_amount,  # TODO: for mining we need to look up the value on the date mined.
                date=trans_date,
            )
        elif op in {transaction.Operation.SPENDING, transaction.Operation.GIFT_SENT}:
            trans = transaction.Transaction(
                operation=op,
                quantity_received=usd_amount,
                symbol_received="USD",
                symbol_traded=curr["Coin"],
                quantity_traded=crypto_amount,
                date=trans_date,
            )
        elif op == transaction.Operation.SELL:
            trans = _make_adhoc_sell(trans_date, crypto_amount, curr)
        return trans


    def __iter__(self):
        return self

def _make_adhoc_sell(date, crypto_amount, curr):
    if curr[RECEIVED_CURRENCY]:
        rcvd_coin = curr[RECEIVED_CURRENCY]
        rcvd_amount = curr[RECEIVED_AMOUNT]
        if not rcvd_amount or not rcvd_coin:
            raise RuntimeError("Invalid row, need currency and amount if either is specified {}".format(curr))
        return transaction.Transaction(transaction.Operation.SELL, symbol_received=rcvd_coin, quantity_received=decimal.Decimal(rcvd_amount), symbol_traded=curr["Coin"], quantity_traded=crypto_amount, date=date)


FORMAT_CLASSES.append(AdhocParser)
