"""
Bybit perpetual PnL.
"""

import decimal

import delorean
import openpyxl

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

_TIMESTAMP_INDEX = 0
_TYPE_INDEX = 2
_AMOUNT_INDEX = 3
_ADDRESS_INDEX = 4

_REQUIRED_HEADERS = ["Time(UTC)", "Coin", "Type", "Amount"]

_TYPE_CELL_CONTENTS = "Realized P&L"


class BybitPNLParser(Format):
    EXCHANGE_HUMAN_READABLE_NAME = "Bybit PnL"
    _EXCHANGE_ID_STR = "bybit"

    @staticmethod
    def needs_binary():
        return True

    def _check_headers(self):
        vals = [cell.value for cell in self._rows[0]]
        for header in _REQUIRED_HEADERS:
            if header not in vals:
                raise ValueError("Required header '{}' not found".format(header))

    def read_transaction(self, line):
        """
        Return None if the row is not taxable.
        """
        try:
            if line[_TYPE_INDEX].value != _TYPE_CELL_CONTENTS:
                return None
            amt = decimal.Decimal(str(line[_AMOUNT_INDEX].value))
            date = delorean.parse(line[_TIMESTAMP_INDEX].value, dayfirst=False).datetime
            # realized profit is measured in BTC
            return transaction.Transaction(
                operation=transaction.Operation.PERPETUAL_PNL,
                quantity_received=amt,
                quantity_traded=0,
                symbol_traded=line[_ADDRESS_INDEX].value,
                symbol_received="BTC",
                date=date,
                fees=decimal.Decimal(0),
                source=self._EXCHANGE_ID_STR,
            )
        except RuntimeError:
            raise RuntimeError("Could not parse bybit data.")
        except KeyError as e:
            raise RuntimeError("Unknown key in bybit file: {}".format(e))

    def __init__(self, open_file):
        self._file = open_file
        open_file.seek(0)
        workbook = openpyxl.load_workbook(open_file)
        self._rows = list(workbook.active.rows)
        self._check_headers()
        self.txs = []
        for line in self._rows[1:]:
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


FORMAT_CLASSES.append(BybitPNLParser)
