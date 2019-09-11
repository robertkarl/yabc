"""
Calculating the cost basis.
"""
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
    # type:  (transaction.Transaction, Decimal, transaction.Transaction) -> transaction.Transaction
    """
    Create a coin to be added back to the pool.

    TODO: For creating an audit trail, we should track the origin of the split
    coin, ie. was it generated from mining, a gift, or purchased?  This could
    be similar to the way we track the origin coin in CBRs.

    :param coin_to_split: a Transaction, either a BUY or an TRADE_INPUT
    :param amount: unsold portion of the asset ie. float(0.3) for a sale of 1 BTC where another coin of 0.7 was already used
    :param trans: the transaction triggering the report
    :return: a Transaction of type SPLIT with a proper basis
    """
    assert isinstance(amount, Decimal)
    assert isinstance(coin_to_split, transaction.Transaction)
    assert isinstance(trans, transaction.Transaction)
    split_amount_back_in_pool = coin_to_split.quantity_received - amount
    fraction_back_in_pool = split_amount_back_in_pool / coin_to_split.quantity_received
    cost = coin_to_split.quantity_traded * fraction_back_in_pool
    fees = coin_to_split.fees * fraction_back_in_pool
    quantity_received = split_amount_back_in_pool
    to_add = transaction.Transaction(
        transaction.Transaction.Operation.SPLIT,
        symbol_received=coin_to_split.symbol_received,
        quantity_received=quantity_received,
        fees=fees,
        symbol_traded=coin_to_split.symbol_traded,
        quantity_traded=cost,
        date=coin_to_split.date,
    )
    assert to_add.quantity_received > 0
    return to_add


def split_report(coin_to_split, amount, trans):
    # type:  (transaction.Transaction, Decimal, transaction.Transaction) -> transaction.Transaction
    """
    The cost basis logic. Note that all fees on buy and sell sides are
    subtracted from the taxable result.

        basis = cost + fees income_subtotal = proceeds - fees taxable_income =
        income_subtotal - basis

    parameters:

        coin_to_split (Transaction): an input. part of this will be the cost
        basis portion of this report

        amount (Float): quantity of the split asset that needs to be sold in
        this report (not the USD).

        trans (Transaction): the transaction triggering this report, a SELL or SPENDING
    """
    assert isinstance(amount, Decimal)
    assert isinstance(coin_to_split, transaction.Transaction)
    assert isinstance(trans, transaction.Transaction)
    assert amount < coin_to_split.quantity_received
    assert not (amount - trans.quantity_received > 1e-5)  # allowed to be equal
    # coin_to_split is a buy, mining, previous split, some kind of input.
    #               quantity_received: crypto amount.
    #               quantity_traded: USD

    # basis and fee (partial amounts of coin_to_split)
    frac_of_basis_coin = amount / coin_to_split.quantity_received
    purchase_price = frac_of_basis_coin * coin_to_split.quantity_traded
    purchase_fee = frac_of_basis_coin * coin_to_split.fees

    # sale proceeds and fee (again, partial amounts of trans)
    frac_of_sale_tx = amount / trans.quantity_traded
    proceeds = (frac_of_sale_tx * trans.quantity_received).quantize(Decimal(".01"))
    sale_fee = (frac_of_sale_tx * trans.fees).quantize(Decimal(".01"))
    return CostBasisReport(
        trans.user_id,
        purchase_price + purchase_fee,
        amount,
        coin_to_split.date,
        proceeds - sale_fee,
        trans.date,
        trans.symbol_traded,
        triggering_transaction=trans,
    )


def process_one(trans, pool):
    # type: (transaction.Transaction, coinpool.CoinPool) -> Sequence
    """
    Cost basis calculator for a single transaction. Return the 'diff'
    required to process this one tx.

    It is assumed that the coin to sell is at the front, at `pool[0]`, so this
    works for both LIFO and FIFO.

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
    if trans.is_simple_input():  # what about: and not trans.is_coin_to_coin():
        diff.add(trans.symbol_received, trans)
        return ([], diff)
    # At this point, trans is a sell

    # TODO: Whenever we use quantity on a SELL transaction, we really mean
    #       quantity_traded. Is this true?
    while amount < trans.quantity_traded:
        pool_index += 1
        amount += pool.get(trans.symbol_traded)[pool_index].quantity_received
    needs_split = (amount - trans.quantity_traded) > 1e-5

    if needs_split:
        coin_to_split = pool.get(trans.symbol_traded)[pool_index]
        excess = amount - trans.quantity_traded
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
        diff.add(coin_to_add.symbol_received, coin_to_add)
    diff.remove(trans.symbol_traded, pool_index)
    if not needs_split:
        pool_index += 1  # Ensures that we report the oldest transaction as a sale.
    if trans.is_taxable_output():
        # The other option is gift. If it's a gift we don't report any gain or loss.
        # The coins just magically remove themselves from the pool.
        # No entry in 8949 for them.
        cost_basis_reports.extend(_build_sale_reports(pool, pool_index, trans))
    return (cost_basis_reports, diff)


def _build_sale_reports(pool, pool_index, trans):
    # type: (coinpool.CoinPool, int, transaction.Transaction) -> Sequence[CostBasisReport]
    """
    Use coins from pool to make CostBasisReports. `trans` is the tx triggering
    the reports. It must be a sell of some kind.
    """
    ans = []
    for i in range(pool_index):
        # each of these including pool_index will become a sale to be reported to IRS
        # The cost basis is pool[i].proceeds
        # The sale price is dependent on the parameter `trans'
        #
        # NOTE: the entire basis coin will be sold; but for each iteration
        # through we only use a portion of trans.

        # curr_basis_tx is a BUY, GIFT_RECEIVED or a TRADE_INPUT, or another input.
        curr_basis_tx = pool.get(trans.symbol_traded)[
            i
        ]  # type: transaction.Transaction
        portion_of_sale = curr_basis_tx.quantity_received / trans.quantity_traded
        # The seller can inflate their cost basis by the buy fees.
        assert curr_basis_tx.symbol_received == trans.symbol_traded
        report = CostBasisReport(
            curr_basis_tx.user_id,
            curr_basis_tx.quantity_traded + curr_basis_tx.fees,
            curr_basis_tx.quantity_received,
            curr_basis_tx.date,
            portion_of_sale * (trans.quantity_received - trans.fees),
            trans.date,
            curr_basis_tx.symbol_received,
            triggering_transaction=trans,
        )
        ans.append(report)
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
    Create a transaction pool, and iteratively process txs.

    Saves the pool state and any cost basis reports.

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
    Given a method and a bunch of transactions, return a list with the
    CostBasisReports calculated.

    TODO: clean this up; we don't need _process_all, process_all, and
    BasisProcessor.
    """
    assert method in coinpool.PoolMethod
    reports, pool = _process_all(method, txs)
    return reports


class BasisProcessor:
    """
    Store state for basis calculations.

    This includes the pool of coins left over at the end of processing the
    given batch.
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
