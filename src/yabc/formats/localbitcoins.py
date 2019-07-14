import csv

from yabc.formats import Format
"""
TXID, Created, Received, Sent, TXtype, TXdesc, TXNotes
,2015-04-05T02:03:47+00:00,1.50000000,,Deposit,
"""

HEADERS = "TXID, Created, Received, Sent, TXtype, TXdesc, TXNotes".split(', ')

class LocalBitcoinsParser(Format):
    EXCHANGE_NAME = "localbitcoins"

    def __init__(self, csv_content=None, filename=None):
        if csv_content:
            assert not filename
            self._file = csv_content
            self._reader = csv.DictReader(csv_content, HEADERS)
        else:
            assert not csv_content
            self._reader = csv.DictReader(open(filename, 'r'), HEADERS)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)

