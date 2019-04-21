"""
Utilities for calculating the cost basis.
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import collections
import copy

from yabc import csv_to_json
from yabc import transaction

SATOSHIS_PER_BITCOIN = int(1e8)


CostBasisReport = collections.namedtuple(
    "CostBasisReport",
    ("descr", "date_acquired", "date_sold", "proceeds", "basis", "gain_or_loss"),
)


def make_cost_basis_report(buy_price, quantity, date_purchased, sale_price, date_sold):
    """
    Should be in the format needed by 8949; dollar amounts are rounded
    """
    descr = "{:.6f} BTC".format(quantity)
    acquired = date_purchased.strftime("%m-%d-%Y")
    sold = date_sold.strftime("%m-%d-%Y")
    proceeds = round(quantity * sale_price)
    basis = round(quantity * buy_price)
    return CostBasisReport(descr, acquired, sold, proceeds, basis, proceeds - basis)


def process_one(trans, pool):
    """
    FIFO cost basis calculator for a single transaction. Return the 'diff'
    required to process this one tx.

    - If transaction is a buy, just return the add-to-pool op.
    - Otherwise, for a sale::
        - Example: buy 0.25 @ $1 and 0.25 at $2. Then sell 0.5 at $3.
                   this is reported to IRS as 2 trannies: 
                   One: Sell 0.25 with a basis of $1
                   Two: Sell 0.25 with a basis of $2
        - Return:
            - ans['remove_index']: The coins up to and including this index will be REMOVED from the pool.
            - ans['basis_reports']: The list of coins to sell, with cost basis filled.
            - ans['add']: At most one coin to add to the pool, if there was a partial sale.

    @param transaction (transaction.Transaction): a buy or sell with fields filled
    @param pool: a sequence containing transaction.Transaction instances.

    @return json describing the transaction:
    {'sell': [T1, T1], 'remove_from_pool': 1, 'add_to_pool': [T5]}
    @TODO
    """
    assert type(trans) is transaction.Transaction and type(pool) is list
    pool = sorted(pool, key=lambda tx: tx.date)
    cost_basis_reports = []
    amount = 0
    pool_index = -1

    if trans.operation == "Buy":
        return {"basis_reports": [], "add": trans, "remove_index": -1}

    while amount < trans.quantity:
        pool_index += 1
        amount += pool[pool_index].quantity
    # TODO we should be using Satoshis for this accounting. We should deal with
    # edge cases such as "transactions rounding to $0.00" elsewhere (when the
    # 8949 is generated.
    needs_split = (amount - trans.quantity) > 1e-5

    to_add = None
    if needs_split:
        coin_to_split = pool[pool_index]
        split_amount_back_in_pool = amount - trans.quantity
        split_amount_to_sell = coin_to_split.quantity - split_amount_back_in_pool

        to_add = copy.deepcopy(coin_to_split)
        split_quantity = to_add.quantity
        to_add.quantity = split_amount_back_in_pool
        to_add.operation = "Split"
        cost_basis_reports.append(
            make_cost_basis_report(
                coin_to_split.usd_subtotal,
                split_amount_to_sell,
                coin_to_split.date,
                trans.usd_subtotal,
                trans.date,
            )
        )

    needs_remove = pool_index
    if not needs_split:
        pool_index += 1  # Ensures that we report the oldest transaction as a sale.
    # TODO it seems like this quantity maybe should be 'pool_index + 1'
    # Consider the case of selling a single bitcoin (without splitting). We will
    # have pool_index==0, and won't call @make_cost_basis_report below.
    for i in range(pool_index):
        # each of these including pool_index will become a sale to be reported to IRS
        # The cost basis is pool[i].proceeds
        # The sale price is dependent on the parameter `trans'
        ir = make_cost_basis_report(
            pool[i].usd_subtotal,
            pool[i].quantity,
            pool[i].date,
            trans.usd_subtotal,
            trans.date,
        )
        cost_basis_reports.append(ir)

    return {
        "basis_reports": cost_basis_reports,
        "add": to_add,
        "remove_index": needs_remove,
    }


def get_all_transactions(coinbase, gemini):
    """
    Get all transactions from a coinbase and a gemini file.

    Arguments:
        coinbase (str): path to coinbase file
        gemini (str): path to gemini file
    """
    cb = csv_to_json.coinbase_to_dict(coinbase) if coinbase else None
    gems = csv_to_json.gemini_to_dict(gemini) if gemini else None
    txs = []
    if gems:
        for i in gems:
            t = transaction.Transaction.FromGeminiJSON(i)
            txs.append(t)
    if cb:
        for i in cb:
            t = transaction.Transaction.FromCoinbaseJSON(i)
            txs.append(t)
    return txs


def process_all(txs):
    """
    Process a list of transactions (which may have been read from coinbase or
    gemini files).

    @return a list of asset sales, each of which has all information necessary
    to report the cost basis to the IRS.
    """
    pool = []
    to_process = sorted(txs, key=lambda tx: tx.date)
    irs_reports = []
    for tx in to_process:
        ops = process_one(tx, pool)
        reports = ops["basis_reports"]
        to_add = ops["add"]
        remove_index = ops["remove_index"]
        if remove_index > -1:
            pool = pool[remove_index + 1 :]
        if to_add is not None:
            # This is where FIFO is defined: put the BUY transactions at the end.
            # For split coins, they need to be sold first.
            if to_add.operation == "Buy":
                pool.append(to_add)
            else:
                assert to_add.operation == "Split"
                pool.insert(0, to_add)
        irs_reports.extend(reports)
    return irs_reports
