import csv
import decimal

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format
from yabc.transaction import Operation

"""
TXID, Created, Received, Sent, TXtype, TXdesc, TXNotes
,2015-04-05T02:03:47+00:00,1.50000000,,Deposit,
"""

HEADERS = "TXID, Created, Received, Sent, TXtype, TXdesc, TXNotes".split(",")


class LocalBitcoinsParser(Format):
    EXCHANGE_NAME = "localbitcoins"

    def __init__(self, csv_content=None, filename=None):
        if csv_content:
            assert not filename
            csv_content.seek(0)
            self._file = csv_content
            self._reader = csv.DictReader(csv_content)
        else:
            assert not csv_content
            self._file = open(filename, "r")
            self._reader = csv.DictReader(self._file, HEADERS)
        self.txs = []
        for line in self._reader:
            if " TXtype" not in line:
                raise ValueError("Invalid LBC, need TXtype header.")
            kind = line[" TXtype"]
            if kind != "Trade":
                continue
            date = delorean.parse(line[" Created"]).datetime
            sent = line[" Sent"]
            rcvd = line[" Received"]
            if sent:
                tx_type = Operation.SELL
                quantity = decimal.Decimal(sent)
            elif rcvd:
                tx_type = Operation.BUY
                quantity = decimal.Decimal(rcvd)
            else:
                raise ValueError("Invalid LBC CSV found.")
            self.txs.append(
                transaction.Transaction(
                    asset_name="BTC", quantity=quantity, operation=tx_type, date=date
                )
            )

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)


FORMAT_CLASSES.append(LocalBitcoinsParser)
