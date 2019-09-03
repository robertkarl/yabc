"""
Calculating the cost basis.
"""
import copy
import csv
import io
from decimal import Decimal
from typing import Sequence

from yabc import coinpool
from yabc import formats
from yabc import transaction
from yabc import transaction_parser
from yabc.costbasisreport import CostBasisReport
from yabc.transaction import Transaction
from yabc.transaction_parser import TransactionParser

__author__ = "Robert Karl <robertkarljr@gmail.com>"


def split_coin_to_add(coin_to_split, amount, trans):
    """
    Create a coin to be added back to the pool.

    TODO: For creating an audit trail, we should track the origin of the split coin,
          ie. was it generated from mining, a gift, or purchased?
    
    parameters:
        amount: unsold portion of the asset ie. float(0.5) for a sale of 1 BTC
                where another coin of 0.5 was already used
        coin_to_split: a Transaction
        trans: the transaction triggering the report
    """
    assert isinstance(amount, Decimal)
    assert isinstance(coin_to_split, transaction.Transaction)
    assert isinstance(trans, transaction.Transaction)
    split_amount_back_in_pool = coin_to_split.quantity_received - amount
    fraction_back_in_pool = split_amount_back_in_pool / coin_to_split.quantity_received
    to_add = copy.deepcopy(coin_to_split)
    to_add.usd_subtotal = coin_to_split.usd_subtotal * fraction_back_in_pool
    to_add.fees = coin_to_split.fees * fraction_back_in_pool
    to_add.quantity_received = split_amount_back_in_pool
    to_add.operation = Transaction.Operation.SPLIT
    assert to_add.quantity_received > 0
    return to_add


def split_report(coin_to_split: Transaction, amount, trans: Transaction):
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
    assert amount < coin_to_split.quantity_received
    assert not (amount - trans.quantity_received > 1e-5)  # allowed to be equal

    # basis and fee (partial amounts of coin_to_split)
    frac_of_basis_coin = amount / coin_to_split.quantity_received
    purchase_price = frac_of_basis_coin * coin_to_split.usd_subtotal
    purchase_fee = frac_of_basis_coin * coin_to_split.fees

    # sale proceeds and fee (again, partial amounts of trans)
    frac_of_sale_tx = amount / trans.quantity_received
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
        triggering_transaction=trans,
    )


def process_one(trans: transaction.Transaction, pool: coinpool.CoinPool):
    """
    Cost basis calculator for a single transaction. Return the 'diff'
    required to process this one tx.

    It is assumed that the coin to sell is at the front, at `pool[0]`, so this works for both
    LIFO and FIFO.

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

    :param trans: a buy or sell with fields filled
    :param pool: a sequence containing transaction.Transaction instances.

    :return (basis_reports, diff): a tuple with any cost basis reports and a PoolDiff.
    """
    diff = coinpool.PoolDiff()
    cost_basis_reports = []
    amount = Decimal(0)
    pool_index = -1
    if trans.is_input():
        diff.add(trans.asset_name, trans)
        return ([], diff)

    # TODO: WHenever we use quantity on a SELL transaction, we really mean quantity_traded. Is this true?
    while amount < trans.quantity_traded:
        pool_index += 1
        amount += pool.get(trans.asset_name)[pool_index].quantity_received
    needs_split = (amount - trans.quantity_received) > 1e-5

    if needs_split:
        coin_to_split = pool.get(trans.asset_name)[pool_index]
        excess = amount - trans.quantity_received
        portion_of_split_coin_to_sell = coin_to_split.quantity_received - excess
        if trans.is_taxable_output():
            # Outgoing gifts would not trigger this.
            # TODO: Alert the user if the value of a gift exceeds $15,000, in which
            #       case gift taxes may be eligible...
            cost_basis_reports.append(
                split_report(coin_to_split, portion_of_split_coin_to_sell, trans)
            )
        coin_to_add = split_coin_to_add(
            coin_to_split, portion_of_split_coin_to_sell, trans
        )
        diff.add(coin_to_add.asset_name, coin_to_add)
    diff.remove(trans.asset_name, pool_index)
    if not needs_split:
        pool_index += 1  # Ensures that we report the oldest transaction as a sale.
    if trans.is_taxable_output():
        # The other option is gift. If it's a gift we don't report any gain or loss.
        # The coins just magically remove themselves from the pool.
        # No entry in 8949 for them.
        cost_basis_reports.extend(_build_sale_reports(pool, pool_index, trans))
    return (cost_basis_reports, diff)


def _build_sale_reports(pool: coinpool.CoinPool, pool_index, trans: Transaction) -> Sequence[CostBasisReport]:
    """
    Use coins from pool to make CostBasisReports. `trans` is the tx triggering the reports.
    """
    ans = []
    for i in range(pool_index):
        # each of these including pool_index will become a sale to be reported to IRS
        # The cost basis is pool[i].proceeds
        # The sale price is dependent on the parameter `trans'
        #
        # NOTE: the entire basis coin will be sold; but for each iteration
        # through we only use a portion of trans.
        curr_basis_tx = pool.get(trans.asset_name)[i]
        portion_of_sale = curr_basis_tx.quantity_received / trans.quantity_traded
        # The seller can inflate their cost basis by the buy fees.
        assert curr_basis_tx.asset_name == trans.asset_name
        ir = CostBasisReport(
            curr_basis_tx.user_id,
            curr_basis_tx.usd_subtotal + curr_basis_tx.fees,
            curr_basis_tx.quantity_received,
            curr_basis_tx.date,
            portion_of_sale * (trans.usd_subtotal - trans.fees),
            trans.date,
            curr_basis_tx.asset_name,
            triggering_transaction=trans,
        )
        ans.append(ir)
    return ans


def transactions_from_file(tx_file, expected_format):
    """
    Get a list of transactions from a single file.

    :param tx_file: the name of a csv file
    :param expected_format: a string, the name of the exchange. (gemini or coinbase)
    """
    hint = None
    if expected_format == "gemini":
        hint = formats.gemini.GeminiParser
        tx_file = io.TextIOWrapper(tx_file)
    elif expected_format == "coinbase":
        hint = formats.coinbase.CoinbaseParser
        tx_file = io.TextIOWrapper(tx_file)
    else:
        tx_file = transaction_parser.TxFile(tx_file, None)
    tx_file = transaction_parser.TxFile(tx_file, hint)
    parser = TransactionParser([tx_file])
    return parser.txs


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


def _process_all(method: coinpool.PoolMethod, txs: Sequence[Transaction]):
    """
    The meat and potatoes. Creates a transaction pool, and iteratively processes txs and saves the pool state and any
    cost basis reports.

    :param method: LIFO or FIFO
    :param txs: a list of transactions (doesn't need to be sorted)
    :return: reports to be sent to tax authorities, and a tx pool.
    """
    assert method in coinpool.PoolMethod
    pool = coinpool.CoinPool(method)
    to_process = sorted(txs, key=lambda tx: tx.date)
    irs_reports = []
    for tx in to_process:
        reports, diff = process_one(tx, pool)
        pool.apply(diff)
        irs_reports.extend(reports)
    return irs_reports, pool


def process_all(method: coinpool.PoolMethod, txs: Sequence[Transaction]):
    """
    Given a method and a bunch of transactions, return a list with the CostBasisReports calculated.
    """
    assert method in coinpool.PoolMethod
    reports, pool = _process_all(method, txs)
    return reports


class BasisProcessor:
    """
    Store state for basis calculations.

    This includes the pool of coins left over at the end of processing the given batch.
    """

    def __init__(self, method, txs):
        assert method in coinpool.PoolMethod
        self.method = method
        self.txs = txs
        self._reports = []

    def process(self) -> Sequence[CostBasisReport]:
        reports, pool = _process_all(self.method, self.txs)
        self._reports = reports
        self.pool = pool
        return self._reports
