"""
Calculating the cost basis.

TODO: Add other accounting methods than FIFO, most notably LIFO.
"""
import copy
import csv
import io
from decimal import Decimal
from typing import Sequence

from yabc import csv_to_json
from yabc import transaction
from yabc.costbasisreport import CostBasisReport
from yabc.transaction import Transaction

__author__ = "Robert Karl <robertkarljr@gmail.com>"


def split_coin_to_add(coin_to_split, amount, trans):
    """
    Create a coin to be added back to the pool.
    
    parameters:
        amount: unsold portion of the asset ie. float(0.5) for a sale of 1 BTC
                where another coin of 0.5 was already used
        coin_to_split: a Transaction
        trans: the transaction triggering the report
    """
    assert isinstance(amount, Decimal)
    assert isinstance(coin_to_split, transaction.Transaction)
    assert isinstance(trans, transaction.Transaction)
    split_amount_back_in_pool = coin_to_split.quantity - amount
    split_fee_back_in_pool = coin_to_split.fees * (
        split_amount_back_in_pool / coin_to_split.quantity
    )
    to_add = copy.deepcopy(coin_to_split)
    to_add.quantity = split_amount_back_in_pool
    to_add.fee = split_fee_back_in_pool
    to_add.operation = "Split"
    assert to_add.quantity > 0
    return to_add


def split_report(coin_to_split, amount, trans):
    """
    The cost basis logic. Note that all fees on buy and sell sides are
    subtracted from the taxable result.

        basis = cost + fees
        income_subtotal = proceeds - fees
        taxable_income = income_subtotal - basis

    parameters:

        coin_to_split (Transaction): part of this will be the cost basis
        portion of this report

        amount (Float): quantity of the split asset that needs to be sold in this report (not the USD).

        trans (Transaction): the transaction triggering this report
    """
    assert isinstance(amount, Decimal)
    assert isinstance(coin_to_split, transaction.Transaction)
    assert isinstance(trans, transaction.Transaction)
    assert amount < coin_to_split.quantity
    assert not (amount - trans.quantity > 1e-5)  # allowed to be equal

    # basis and fee (partial amounts of coin_to_split)
    frac_of_basis_coin = amount / coin_to_split.quantity
    purchase_price = frac_of_basis_coin * coin_to_split.usd_subtotal
    purchase_fee = frac_of_basis_coin * coin_to_split.fees

    # sale proceeds and fee (again, partial amounts of trans)
    frac_of_sale_tx = amount / trans.quantity
    proceeds = (frac_of_sale_tx * trans.usd_subtotal).quantize(Decimal(".01"))
    sale_fee = (frac_of_sale_tx * trans.fees).quantize(Decimal(".01"))
    return CostBasisReport(
        trans.user_id,
        purchase_price + purchase_fee,
        amount,
        coin_to_split.date,
        proceeds - sale_fee,
        trans.date,
        trans.asset_name,
    )


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
    """
    assert type(trans) is transaction.Transaction and type(pool) is list
    pool = sorted(pool, key=lambda tx: tx.date)
    cost_basis_reports = []
    amount = Decimal(0)
    pool_index = -1

    if trans.operation == Transaction.Operation.BUY:
        return {"basis_reports": [], "add": trans, "remove_index": -1}

    while amount < trans.quantity:
        pool_index += 1
        amount += pool[pool_index].quantity
    needs_split = (amount - trans.quantity) > 1e-5

    to_add = None
    if needs_split:
        coin_to_split = pool[pool_index]
        excess = amount - trans.quantity
        portion_of_split_coin_to_sell = coin_to_split.quantity - excess
        cost_basis_reports.append(
            split_report(coin_to_split, portion_of_split_coin_to_sell, trans)
        )
        to_add = split_coin_to_add(coin_to_split, portion_of_split_coin_to_sell, trans)
    needs_remove = pool_index
    if not needs_split:
        pool_index += 1  # Ensures that we report the oldest transaction as a sale.
    if trans.operation == Transaction.Operation.SELL:
        # The other option is gift. If it's a gift we don't report any gain or loss.
        # The coins just magically remove themselves from the pool.
        # No entry in 8949 for them.
        cost_basis_reports.extend(_build_sale_reports(pool, pool_index, trans))

    return {
        "basis_reports": cost_basis_reports,
        "add": to_add,
        "remove_index": needs_remove,
    }


def _build_sale_reports(pool, pool_index, trans):
    ans = []
    for i in range(pool_index):
        # each of these including pool_index will become a sale to be reported to IRS
        # The cost basis is pool[i].proceeds
        # The sale price is dependent on the parameter `trans'
        #
        # NOTE: the entire basis coin will be sold; but for each iteration
        # through we only use a portion of trans.
        portion_of_sale = pool[i].quantity / trans.quantity
        ir = CostBasisReport(
            pool[i].user_id,
            pool[i].usd_subtotal + pool[i].fees,
            pool[i].quantity,
            pool[i].date,
            portion_of_sale * (trans.usd_subtotal - trans.fees),
            trans.date,
            pool[i].asset_name,
        )
        ans.append(ir)
    return ans


def transactions_from_file(tx_file, expected_format):
    if expected_format == "gemini":
        return csv_to_json.txs_from_gemini(io.TextIOWrapper(tx_file))
    elif expected_format == "coinbase":
        return csv_to_json.txs_from_coinbase(io.TextIOWrapper(tx_file))
    raise ValueError("unknown format {}".format(expected_format))


def get_all_transactions(coinbase, gemini):
    """
    Get all transactions from a coinbase and a gemini file.

    TODO: Accept arbitrary (filename, format) pairs

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


def reports_to_csv(reports: Sequence[CostBasisReport]):
    """ Return a file-like object with a row for each report.

    Also includes summary information and headers.
    """

    of = io.StringIO()
    writer = csv.writer(of)
    names = CostBasisReport.field_names()
    writer.writerow(names)
    for r in reports:
        writer.writerow(r.fields())
    writer.writerow(["total", "{}".format(sum([i.gain_or_loss for i in reports]))])
    of.seek(0)
    return of


def process_all(method, txs):
    if method == "FIFO":
        return process_all_fifo(txs)
    raise ValueError("Invalid method {}".format(method))


def process_all_fifo(txs):
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
            if to_add.operation == Transaction.Operation.BUY:
                pool.append(to_add)
            else:
                assert to_add.operation == Transaction.Operation.SPLIT
                pool.insert(0, to_add)
        irs_reports.extend(reports)
    return irs_reports
