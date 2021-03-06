"""
Code for importing data from a report generated by the exchange Coinbase.

YABC is not affiliated with the company Coinbase or any of its products.
"""
import csv
import decimal

from dateutil import parser

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format


def from_coinbase(f):
    """
    :param f: a file-like object with csv data.
    @return dictionaries with coinbase fields
    """
    f.seek(0)
    rawcsv = [i for i in csv.reader(f)]
    if len(rawcsv) < 5:
        raise RuntimeError("Invalid CSV file, not enough rows.")
    fieldnames = rawcsv[4]
    if not len(fieldnames) >= 2 or not fieldnames[-2].count("Coinbase") > 0:
        raise RuntimeError("Invalid coinbase file encountered")
    fieldnames[-1] = "Bitcoin Hash"
    fieldnames[-2] = "Coinbase ID"
    f.seek(0)
    transactions = [i for i in csv.DictReader(f, fieldnames)]
    # Previously, coinbase column 4 had timestamp.  Documents generated as
    # of April 2019 have it as the first column.
    # First meaningful row is 4; 3 has headers so we can check that.
    assert transactions[3]["Timestamp"] == "Timestamp"
    transactions = transactions[4:]
    for i in transactions:
        assert "Coinbase ID" in i
        i["Site"] = "Coinbase"
    USD_and_back = [
        i
        for i in transactions
        if (i["Transfer Total"] is not "" and i["Transfer Total"] is not None)
    ]
    return USD_and_back


def txs_from_coinbase(f):
    """
    :param f: a filelike object with CSV data
    :return: a list of transaction.Transaction
    """
    dicts = from_coinbase(f)
    return [FromCoinbaseJSON(i) for i in dicts]


class CoinbaseParser(Format):
    FORMAT_NAME = "Coinbase (Trades Format)"
    EXCHANGE_HUMAN_READABLE_NAME = "Coinbase"
    _EXCHANGE_ID_STR = "coinbase"

    def __init__(self, file_or_fname):
        self._file = file_or_fname
        self._reports = []
        if isinstance(file_or_fname, str):
            with open(file_or_fname) as f:
                self._reports = txs_from_coinbase(f)
        else:
            self._reports = txs_from_coinbase(file_or_fname)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._reports:
            raise StopIteration
        return self._reports.pop(0)


def FromCoinbaseJSON(json):
    """
    Arguments:
        json (dict): a coinbase-style dictionary with the following fields:
            - 'Transfer Total': the total USD price, including fees.
            - 'Transfer Fee': the USD fee charged by the exchange.
            - 'Amount': the amount of bitcoin sold. (It's negative for sales.)
            - 'Currency': which cryptocurrency was involved.
            - 'Timestamp': 'hour:min:sec.millisecs' formatted timestamp.
    Returns: Transaction instance with important fields populated
    """
    operation = transaction.Transaction.Operation.BUY
    proceeds = json["Transfer Total"]
    fee = json["Transfer Fee"]
    asset_name = json["Currency"]
    quantity = decimal.Decimal(json["Amount"])
    if quantity < 0:
        operation = transaction.Transaction.Operation.SELL
        quantity = abs(quantity)
    timestamp_str = json["Timestamp"]
    return transaction.Transaction(
        asset_name=asset_name,
        operation=operation,
        quantity=quantity,
        date=parser.parse(timestamp_str),
        fees=fee,
        source="coinbase",
        usd_subtotal=proceeds,
    )


FORMAT_CLASSES.append(CoinbaseParser)
