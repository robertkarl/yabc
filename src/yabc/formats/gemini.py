"""
TODO: Accept Gemini .xlsx files. Do not require the user to convert to CSV.
"""
import csv
import decimal

import delorean

from yabc import formats
from yabc import transaction

_CURRENCIES = ["BCH", "BTC", "ZEC", "ETH", "LTC"]
_SOURCE_NAME = "gemini"
_TIME_HEADER = "Time (UTC)"
_TYPE_HEADER = "Type"


def _gem_int_from_dollar_string(s):
    s = s.strip(" $()")
    s = s.replace(",", "")
    return decimal.Decimal(s)


def _quantity(tx_row):
    """
    :return: a decimal.Decimal with the quantity of eth, btc, etc traded.
    """
    # Currency field looks like 'BTCUSD'
    currency = tx_row["Symbol"].rstrip("USD")
    if currency not in _CURRENCIES:
        raise RuntimeError("Currency {} not supported!".format(currency))

    column_name = "{} Amount {}".format(currency, currency)
    return decimal.Decimal(tx_row[column_name].strip("(").split(" ")[0])


def _tx_from_gemini_row(tx_row):
    """
    Create a Transaction based on a row. May return None.

    :param tx: a dictionary with keys from a gemini transaction history spreadsheet.
    :return:  None if not a transaction needed for taxes. Otherwise a Transaction object.
    """
    if _TYPE_HEADER not in tx_row:
        raise RuntimeError("Not a valid gemini file.")
    if tx_row[_TYPE_HEADER] not in ("Buy", "Sell"):
        return None
    tx = transaction.Transaction(_gemini_type_to_operation(tx_row["Type"]))
    tx.date = delorean.parse(
        "{} {}".format(tx_row["Date"], tx_row[_TIME_HEADER]), dayfirst=False
    ).datetime
    tx.quantity_received = _gem_int_from_dollar_string(tx_row["USD Amount USD"])
    tx.fees = _gem_int_from_dollar_string(tx_row["Fee (USD) USD"])
    tx.quantity_traded = _quantity(tx_row)
    tx.market_name = tx_row['Symbol']
    tx.source = _SOURCE_NAME
    return tx


def _read_txs_from_file(f):
    """
    Validate headers and read buy/sell transactions from the open file-like object 'f'.

    Note: we use the seek method on f.
    """
    f.seek(0)
    rawcsv = [i for i in csv.reader(f)]
    if not rawcsv:
        raise RuntimeError("not enough rows in gemini file {}".format(f))
    fieldnames = rawcsv[0]
    _valid_gemini_headers(fieldnames)
    f.seek(0)
    transactions = [i for i in csv.DictReader(f, fieldnames)][1:]
    ans = []
    for row in transactions:
        item = _tx_from_gemini_row(row)
        if item is not None:
            ans.append(item)
    return ans


def _valid_gemini_headers(fieldnames):
    """
    Make sure we have the required headers to be sure this is a gemini file.
    """
    required_fields = "Type,Date,Time (UTC),Symbol,BTC Amount BTC,USD Amount USD,Fee (USD) USD".split(
        ","
    )
    for field in required_fields:
        if field not in fieldnames:
            raise RuntimeError(
                "Not a valid gemini file. Requires header '{}'".format(field)
            )


class GeminiParser(formats.Format):
    def __init__(self, fname_or_file):
        self.txs = []
        self.flags = []
        self._file = fname_or_file
        if isinstance(fname_or_file, str):
            with open(fname_or_file) as f:
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
