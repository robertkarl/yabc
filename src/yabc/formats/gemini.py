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
    return (decimal.Decimal(tx_row[column_name].strip("(").split(" ")[0]), currency)


def _tx_from_gemini_row(tx_row):
    """
    Create a Transaction based on a row. May return None.

    :param tx_row: a dictionary with keys from a gemini transaction history spreadsheet.
    :return:  None if not a transaction needed for taxes. Otherwise a Transaction object.
    """
    if _TYPE_HEADER not in tx_row:
        raise RuntimeError("Not a valid gemini file.")
    if tx_row[_TYPE_HEADER] not in ("Buy", "Sell"):
        return None
    date = delorean.parse(
        "{} {}".format(tx_row["Date"], tx_row[_TIME_HEADER]), dayfirst=False
    ).datetime
    usd_subtotal = _gem_int_from_dollar_string(tx_row["USD Amount USD"])
    fees = _gem_int_from_dollar_string(tx_row["Fee (USD) USD"])
    quantity, currency = _quantity(tx_row)
    quantity = quantity
    tp = _gemini_type_to_operation(tx_row["Type"])
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
    FORMAT_NAME = "Gemini CSV"
    EXCHANGE_HUMAN_READABLE_NAME = "Gemini"
    _EXCHANGE_ID_STR = "gemini"

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
