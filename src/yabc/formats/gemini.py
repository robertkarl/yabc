import csv
import decimal

import dateutil

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format


def gem_int_from_dollar_string(s):
    s = s.strip(" $()")
    s = s.replace(",", "")
    return decimal.Decimal(s)


def clean_gemini_row(tx):
    # assert type(tx) is OrderedDict # not true with python3.5.2
    if "Type" not in tx:
        raise RuntimeError("Not a valid gemini file.")
    if tx["Type"] not in ("Buy", "Sell"):
        return None
    ans = {}
    ans["Type"] = tx["Type"]
    ans["Date"] = dateutil.parser.parse(tx["Date"])
    ans["BTC Amount"] = tx["BTC Amount BTC"].strip("(").split(" ")[0]
    usd_str = gem_int_from_dollar_string(tx["USD Amount USD"])
    ans["USD Amount"] = usd_str
    ans["USD Fee"] = gem_int_from_dollar_string(tx["Fee (USD) USD"])
    ans["Site"] = "Gemini"
    return ans


def from_gemini(f):
    f.seek(0)
    rawcsv = [i for i in csv.reader(f)]
    if not rawcsv:
        raise RuntimeError("not enough rows in gemini file {}".format(f))
    fieldnames = rawcsv[0]
    valid_gemini_headers(fieldnames)
    f.seek(0)
    ts = [i for i in csv.DictReader(f, fieldnames)]
    ts = ts[1:]
    ans = []
    for tx in ts:
        item = clean_gemini_row(tx)
        if item is not None:
            ans.append(item)
    return [i for i in ans if i["Type"] == "Buy" or i["Type"] == "Sell"]


def valid_gemini_headers(fieldnames):
    required_fields = "Type,Date,BTC Amount BTC,USD Amount USD,Fee (USD) USD".split(",")
    for field in required_fields:
        if field not in fieldnames:
            raise RuntimeError(
                "Not a valid gemini file. Requires header '{}'".format(field)
            )


def gemini_to_dict(fname):
    with open(fname, "r") as f:
        return from_gemini(f)
    return None


def fname_to_tx_gemini(fname: str):
    gems = gemini_to_dict(fname) if fname else None
    txs = []
    for g in gems:
        t = FromGeminiJSON(g)
        txs.append(t)
    return txs


class GeminiParser(Format):
    EXCHANGE_NAME = "Gemini"

    def __init__(self, fname_or_file):
        self.txs = []
        self.flags = []
        self._file = fname_or_file
        if isinstance(fname_or_file, str):
            self.txs = fname_to_tx_gemini(fname_or_file)
        else:
            tx_dicts = from_gemini(fname_or_file)
            self.txs = [FromGeminiJSON(i) for i in tx_dicts]

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)


def txs_from_gemini(f):
    dicts = from_gemini(f)
    return [FromGeminiJSON(i) for i in dicts]


def gemini_type_to_operation(gemini_type: str):
    if gemini_type == "Buy":
        return transaction.Transaction.Operation.BUY
    elif gemini_type == "Sell":
        return transaction.Transaction.Operation.SELL
    raise RuntimeError(
        "Invalid Gemini transaction type {} encountered.".format(gemini_type)
    )


def FromGeminiJSON(json):
    """
    Arguments
        json (Dictionary):
    """

    operation = gemini_type_to_operation(json["Type"])
    quantity = json["BTC Amount"]
    usd_total = json["USD Amount"]
    fee = json["USD Fee"]
    timestamp_str = "{}".format(json["Date"])
    return transaction.Transaction(
        asset_name="BTC",
        operation=operation,
        quantity=quantity,
        fees=fee,
        date=dateutil.parser.parse(timestamp_str),
        source="gemini",
        usd_subtotal=usd_total,
    )


FORMAT_CLASSES.append(GeminiParser)
