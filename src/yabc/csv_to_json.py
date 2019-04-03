"""
Convert coinbase or gemini files to json.
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

from collections import OrderedDict
import csv
import sys

from dateutil import parser

"""
['Date', 'BTC Amount', 'USD Fee', 'Type', 'USD Amount', 'Site', 'Cost Basis']

"""

def round_to_int(somefloat):
    assert type(somefloat) is float
    if somefloat % 1 > 0.5:
        return int(somefloat) + 1
    return int(somefloat)


def gem_int_from_dollar_string(s):
    s = s.strip(" $()")
    s = s.replace(",", "")
    return round_to_int(float(s))


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
    assert type(fname) is str
    fieldnames = []
    rawcsv = [i for i in csv.reader(open(fname))]
    fieldnames = rawcsv[0]
    with open(fname) as f:
        ts = [i for i in csv.DictReader(f, fieldnames)]
        ts = ts[1:]
        ans = []
        for tx in ts:
            item = clean_gemini_row(tx)
            if item is not None:
                ans.append(item)
        return [i for i in ans if i["Type"] == "Buy" or i["Type"] == "Sell"]
    return []


def coinbase_to_dict(fname):
    filename = fname
    with open(filename) as f:  # TODO don't open and read this file twice
        rawcsv = [i for i in csv.reader(f)]

        fieldnames = rawcsv[4]
        assert fieldnames[-2].count("Coinbase") > 0
        fieldnames[-1] = "Bitcoin Hash"
        fieldnames[-2] = "Coinbase ID"

    with open(filename) as f:
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
    return []


def get_transactions_to_USD(fname, exchange):
    if exchange == "coinbase":
        return coinbase_to_dict(fname)
    elif exchange == "gemini":
        return gemini_to_dict(fname)
    assert false
