"""
Convert coinbase or gemini files to json.
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import csv
import decimal

from dateutil import parser

from yabc import transaction
from yabc.formats import coinbase


"""
['Date', 'BTC Amount', 'USD Fee', 'Type', 'USD Amount', 'Site', 'Cost Basis']

"""


def gem_int_from_dollar_string(s):
    s = s.strip(" $()")
    s = s.replace(",", "")
    return decimal.Decimal(s)


def clean_gemini_row(tx):
    # assert type(tx) is OrderedDict # not true with python3.5.2
    if tx["Type"] not in ("Buy", "Sell"):
        return None
    ans = {}
    ans["Type"] = tx["Type"]
    ans["Date"] = parser.parse(tx["Date"])
    ans["BTC Amount"] = tx["BTC Amount BTC"].strip("(").split(" ")[0]
    usd_str = gem_int_from_dollar_string(tx["USD Amount USD"])
    ans["USD Amount"] = usd_str
    ans["USD Fee"] = gem_int_from_dollar_string(tx["Trading Fee (USD) USD"])
    ans["Site"] = "Gemini"
    return ans


def gemini_to_dict(fname):
    f = open(fname, "r")
    return from_gemini(f)


def txs_from_gemini(f):
    dicts = from_gemini(f)
    return [transaction.Transaction.FromGeminiJSON(i) for i in dicts]


def from_gemini(f):
    f.seek(0)
    rawcsv = [i for i in csv.reader(f)]
    if not rawcsv:
        raise RuntimeError("not enough rows in gemini file {}".format(f))
    fieldnames = rawcsv[0]
    f.seek(0)
    ts = [i for i in csv.DictReader(f, fieldnames)]
    ts = ts[1:]
    ans = []
    for tx in ts:
        item = clean_gemini_row(tx)
        if item is not None:
            ans.append(item)
    return [i for i in ans if i["Type"] == "Buy" or i["Type"] == "Sell"]


def get_transactions_to_USD(fname, exchange):
    if exchange == "coinbase":
        return coinbase.coinbase_to_dict(fname)
    elif exchange == "gemini":
        return gemini_to_dict(fname)
    assert False
