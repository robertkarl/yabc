"""
Calculate the cost basis.
"""
import csv
import decimal
import io
from decimal import Decimal
from typing import Sequence

from yabc import coinpool
from yabc import ohlcprovider
from yabc import transaction
from yabc.costbasisreport import CostBasisReport
from yabc.transaction import Transaction
from yabc.transaction import is_fiat

__author__ = "Robert Karl <robertkarljr@gmail.com>"


def _split_coin_to_add(coin_to_split, amount, trans):
    # type:  (transaction.Transaction, Decimal, transaction.Transaction) -> transaction.Transaction
    """
    Create a coin to be added back to the pool.

    TODO: For creating an audit trail, we should track the origin of the split
      coin, ie. was it generated from mining, a gift, or purchased?  This could
      be similar to the way we track the origin coin in CBRs.

    :param coin_to_split: a Transaction, either a BUY or an TRADE_INPUT

    :param amount: unsold portion of the asset ie. float(0.3) for a sale of 1
    BTC where another coin of 0.7 was already used

    :param trans: the transaction triggering the report

    :return: a Transaction of type SPLIT with a proper basis
    """
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

    :param coin_to_split:  an input. part of this will be the cost basis portion of this report
    
    :param amount:  quantity of the split asset that needs to be sold in this report (not the USD).
    
    :param trans: the transaction triggering this report, a SELL or SPENDING

    :return: a transaction of type Split
    """
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


def _process_one(trans, pool, ohlc_source=None):
    # type: (transaction.Transaction, coinpool.CoinPool, ohlcprovider.OhlcProvider) -> Sequence
    """
    Cost basis calculator for a single transaction. Return the 'diff'
    required to process this one tx.

    It is assumed that the coin to sell is at the front, at `pool[0]`, so this
    works for both LIFO and FIFO.

    - If transaction is a buy, just return the add-to-pool op.
    - Otherwise, for a sale::
        - Example: buy 0.25 @ $1 and 0.25 at $2. Then sell 0.5 at $3.
                   this is reported to IRS as 2 transactions:
                   One: Sell 0.25 with a basis of $1
                   Two: Sell 0.25 with a basis of $2

    :param trans: a buy or sell with fields filled
    :param pool: a sequence containing transaction.Transaction instances.

    :return (reports, diff, flags): any CostBasisReports, the PoolDiff, any flags raised.
    """
    diff = coinpool.PoolDiff()
    flags = []
    cost_basis_reports = []
    basis_information_absent = False
    amount = Decimal(0)
    pool_index = -1
    if trans.is_simple_input():  # what about: and not trans.is_coin_to_coin():
        diff.add(trans.symbol_received, trans)
        return ([], diff, [])
    # At this point, trans is a sell

    # TODO: Whenever we use quantity on a SELL transaction, we really mean
    #       quantity_traded. Is this true?
    while amount < trans.quantity_traded:
        pool_index += 1
        curr_pool = pool.get(trans.symbol_traded)
        if pool_index >= len(curr_pool):
            # If we get here, we have partial information about the tx.
            # We should probably use a basis of zero for the sale.
            flags.append(("Transaction without basis information", trans))
            basis_information_absent = True
            amount = trans.quantity_traded
        else:
            amount += curr_pool[pool_index].quantity_received
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
        coin_to_add = _split_coin_to_add(
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
        cost_basis_reports.extend(
            _build_sale_reports(pool, pool_index, trans, basis_information_absent)
        )
    return (cost_basis_reports, diff, flags)


def _build_sale_reports(pool, pool_index, trans, basis_information_absent):
    # type: (coinpool.CoinPool, int, transaction.Transaction) -> Sequence[CostBasisReport]
    """
    Use coins from pool to make CostBasisReports. `trans` is

    :param trans: the tx triggering the reports. It must be a sell of some kind.
    """
    ans = []
    if basis_information_absent:
        report = CostBasisReport(
            trans.user_id,
            decimal.Decimal(0),
            trans.quantity_traded,
            trans.date,
            proceeds=trans.quantity_received,
            date_sold=trans.date,
            asset=trans.symbol_traded,
            triggering_transaction=trans,
        )
        return [report]
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
        if not is_fiat(trans.symbol_received):
            raise RuntimeError(
                "Need fiat values when building CostBasisReports. Triggering sale tx: {}".format(
                    trans
                )
            )
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


def _process_all(method, txs, ohlc_source=None):
    # type: (coinpool.PoolMethod, Sequence[Transaction], ohlcprovider.OhlcProvider) -> Sequence
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
    flags = []
    for tx in to_process:
        reports, diff, curr_flags = _process_one(tx, pool, ohlc_source)
        flags.extend(curr_flags)
        pool.apply(diff)
        irs_reports.extend(reports)
    return irs_reports, pool, flags


class BasisProcessor:
    """
    Store state for basis calculations.

    This includes the pool of coins left over at the end of processing the
    given batch.

    See self.pool and self.flags after running process()
    """

    def __init__(self, method, txs, ohlc_class=ohlcprovider.OhlcProvider):
        # type: (coinpool.PoolMethod, Sequence, type) -> None
        self.ohlc = ohlc_class()
        self._method = method
        self._txs = txs
        self._reports = []
        self.pool = []
        self._flags = None

    def flags(self):
        if self._flags is None:
            raise RuntimeError("Run basis calculation first")
        return self._flags

    def process(self):
        # type: () -> Sequence[CostBasisReport]
        """
        Perform the basis calculation given the txs passed to the constructor.

        Saves the pool of remaining coins to self.pool.

        :return: the CostBasisReports generated.
        """
        reports, pool, flags = _process_all(self._method, self._txs, self.ohlc)
        self._reports = reports
        self.pool = pool
        self._flags = flags
        return self._reports
