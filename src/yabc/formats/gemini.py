import decimal

import openpyxl

from yabc import formats
from yabc import transaction

_CURRENCIES = ["BCH", "BTC", "ZEC", "ETH", "LTC"]
_SOURCE_NAME = "gemini"
_TIME_HEADER = "Time (UTC)"
_TYPE_HEADER = "Type"

_GEM_HEADERS = ["Date", _TIME_HEADER, _TYPE_HEADER, "Symbol", "Specification"]

_PAIR_INDEX = 3
_TYPE_INDEX = 2
_AMOUNT_INDEX = 7
_USD_FEE = 8

_ROWS = []


def _quantity(tx_row):
    """
    :return: a decimal.Decimal, str tuple with the quantity of eth, btc, etc traded.
    """
    supported = [(10, "BTC"), (13, "ETH"), (16, "ZEC"), (19, "BCH"), (22, "LTC")]
    for index, currency_name in supported:
        if tx_row[index].value:
            return abs(decimal.Decimal(str(tx_row[index].value))), currency_name
    raise RuntimeError("Could not parse any cryptocurrency from Gemini row")


def _tx_from_gemini_row(tx_row):
    """
    Create a Transaction based on a row. May return None.

    :param tx_row: a dictionary with keys from a gemini transaction history spreadsheet.
    :return:  None if not a transaction needed for taxes. Otherwise a Transaction object.
    """
    if tx_row[_TYPE_INDEX].value not in ("Buy", "Sell"):
        return None
    date = tx_row[0].value
    usd_subtotal = abs(decimal.Decimal(str(tx_row[_AMOUNT_INDEX].value)))
    fees = abs(decimal.Decimal(str(tx_row[_USD_FEE].value)))
    quantity, currency = _quantity(tx_row)
    quantity = quantity
    tp = _gemini_type_to_operation(tx_row[_TYPE_INDEX].value)
    if tp == transaction.Operation.BUY:
        tx = transaction.Transaction(
            operation=tp,
            quantity_traded=usd_subtotal,
            symbol_traded="USD",
            quantity_received=quantity,
            symbol_received=currency,
            date=date,
            fees=fees,
            source=_SOURCE_NAME,
        )
    elif tp == transaction.Operation.SELL:
        tx = transaction.Transaction(
            operation=tp,
            quantity_traded=quantity,
            symbol_traded=currency,
            quantity_received=usd_subtotal,
            symbol_received="USD",
            date=date,
            fees=fees,
            source=_SOURCE_NAME,
        )
    else:
        raise RuntimeError("Unknown transaction type from gemini file.")
    return tx


def _validate_header(row):
    sheet_headers = [i.value for i in row]
    for header in _GEM_HEADERS:
        if header not in sheet_headers:
            raise ValueError("Gemini required headers not found '{}'".format(header))


def _read_txs_from_file(f):
    """
    Validate headers and read buy/sell transactions from the open file-like object 'f'.

    Note: we use the seek method on f.
    """
    ans = []
    f.seek(0)
    workbook = openpyxl.load_workbook(f)
    sheet = workbook.active
    all_contents = list(sheet.rows)
    _validate_header(all_contents[0])
    contents = all_contents[1:]
    for row in contents:
        item = _tx_from_gemini_row(row)
        if item is not None:
            ans.append(item)
    return ans


class GeminiParser(formats.Format):
    FORMAT_NAME = "Gemini CSV"
    EXCHANGE_HUMAN_READABLE_NAME = "Gemini"
    _EXCHANGE_ID_STR = "gemini"

    @staticmethod
    def needs_binary():
        return True

    def __init__(self, fname_or_file):
        """
        For gemini, which uses XLSX, the open file must be either in binary mode, or the name of a file for openpyxl.
        :param fname_or_file:
        """
        self.txs = []
        self.flags = []
        self._file = fname_or_file
        if isinstance(fname_or_file, str):
            with open(fname_or_file, "br") as f:
                self.txs = _read_txs_from_file(f)
        else:
            # it must be an open file
            self.txs = _read_txs_from_file(fname_or_file)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)


def _gemini_type_to_operation(gemini_type: str):
    if gemini_type == "Buy":
        return transaction.Transaction.Operation.BUY
    elif gemini_type == "Sell":
        return transaction.Transaction.Operation.SELL
    raise RuntimeError(
        "Invalid Gemini transaction type {} encountered.".format(gemini_type)
    )


formats.FORMAT_CLASSES.append(GeminiParser)
