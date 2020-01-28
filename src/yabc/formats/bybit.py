"""
Bybit perpetual PnL.
"""

import csv
import datetime
import decimal

import delorean
import openpyxl

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

_TYPE_INDEX = 2
_AMOUNT_INDEX = 3
_ADDRESS_INDEX = 4

_REQUIRED_HEADERS = [
    "Time(UTC)"
]

_PNL_CELL_CONTENTS = 'Realized P&L'


class BybitPNLParser(Format):
    EXCHANGE_HUMAN_READABLE_NAME = "Bybit PnL"
    _EXCHANGE_ID_STR = "bybit"

    @staticmethod
    def needs_binary():
        return True

    def read_transaction(self, line):
        """
        Return None if the row is not taxable.
        """
        try:
            kind = transaction.Operation.SELL
            date = delorean.parse(line[_TIMESTAMP_HEADER], dayfirst=False).datetime
            if date == self._last_date:
                date += self._trade_time_delta
            self._last_date = date
            symbol_traded = "Bybit {}".format(line[_ADDRESS_HEADER])
            # realized profit is measured in microBTC. ie. a realized profit of 1e6 is 1BTC
            quantity_received = decimal.Decimal(line[_FIAT_TRANSACTED_HEADER]) / decimal.Decimal(1e6)
            return transaction.Transaction(
                operation=kind,
                quantity_received=quantity_received,
                quantity_traded=0,
                symbol_traded=symbol_traded,
                symbol_received="BTC",
                date=date,
                fees=decimal.Decimal(0),
                source=self._EXCHANGE_ID_STR,
            )
        except RuntimeError:
            raise RuntimeError("Could not parse BitMEX data.")
        except KeyError as e:
            raise RuntimeError("Unknown key in BitMEX file: {}".format(e))

    def __init__(self, open_file):
        self._last_date = None
        self._trade_time_delta = datetime.timedelta(seconds=1)
        open_file.seek(0)
        self._reader = openpyxl.load_workbook(open_file)
        self._file = open_file
        self.txs = []
        for line in self._reader:
            tx = self.read_transaction(line)
            if tx is not None:
                self.txs.append(tx)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)

    def cleanup(self):
        try:
            self._file.close()
        except:
            pass


FORMAT_CLASSES.append(BitMEXParser)
