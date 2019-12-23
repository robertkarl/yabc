"""
Adhoc transactions - yabc's proprietary format for specifying trades, mining,
espending, and gifts.
"""
import csv
import datetime
import decimal

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

_TRANSACTION_TYPE_HEADER = "Type"
_RECEIVED_CURRENCY = "ReceivedCurrency"
_TIMESTAMP_HEADER = "Timestamp"
_RECEIVED_AMOUNT = "ReceivedAmount"
_TRADED_CURRENCY = "TradedCurrency"
_TRADED_AMOUNT = "TradedAmount"
_FEE = "Fee"
_FEE_COIN = "FeeCurrency"

_FIELD_NAMES = [
    _RECEIVED_CURRENCY,
    _RECEIVED_AMOUNT,
    _TIMESTAMP_HEADER,
    _TRANSACTION_TYPE_HEADER,
    _TRADED_CURRENCY,
    _TRADED_AMOUNT,
    _FEE,
    _FEE_COIN,
]

_SUPPORTED = [
    transaction.Transaction.Operation.GIFT_RECEIVED,
    transaction.Transaction.Operation.GIFT_SENT,
    transaction.Transaction.Operation.MINING,
    transaction.Transaction.Operation.SPENDING,
    transaction.Transaction.Operation.SELL,
    transaction.Transaction.Operation.BUY,
]


class AdhocParser(Format):
    """
    Defines an input format for ad-hoc transactions like mining, spending, and gifts.

    This class translates CSV rows into transaction objects.
    """

    FORMAT_NAME = "adhoc CSV"
    EXCHANGE_HUMAN_READABLE_NAME = "adhoc"
    _EXCHANGE_ID_STR = "adhoc"

    def validate_headers(self, curr):
        for header_name in _FIELD_NAMES:
            if header_name not in curr:
                raise RuntimeError(
                    "Incorrectly formatted adhoc file {}, missing header key {}".format(
                        self._file, header_name
                    )
                )

    def __init__(self, csv_file):
        """
        :param csv_file: can be a list of rows, each containing a string, or an
        open file-like object.
        """
        self._file = None
        assert not isinstance(csv_file, str)
        if isinstance(csv_file, (list, tuple)):
            self.validate_headers(csv_file[0])
        else:
            csv_file.seek(0)
            contents = []
            while True:
                line = csv_file.readline()
                if line:
                    contents.append(line)
                else:
                    break
            rawcsv = list(csv.reader(contents))
            if not rawcsv:
                raise RuntimeError("not enough rows in adhoc file {}".format(csv_file))
            fieldnames = rawcsv[0]
            self.validate_headers(fieldnames)
            csv_file.seek(0)
        self._file = csv_file
        self.reader = csv.DictReader(self._file)

    def __next__(self):
        curr = next(self.reader)
        if not curr:
            raise StopIteration
        op = None
        for t in _SUPPORTED:
            if curr[_TRANSACTION_TYPE_HEADER].upper() == t.value.upper():
                op = t
        if not op:
            return transaction.Transaction(operation=transaction.Operation.NOOP)
        trans_date = delorean.parse(curr[_TIMESTAMP_HEADER], dayfirst=False).datetime

        if op == transaction.Operation.MINING:
            return _handle_mining(trans_date, curr)
        elif op == transaction.Operation.GIFT_RECEIVED:
            return _handle_gift_received(trans_date, curr)
        elif op == transaction.Operation.SPENDING:
            return _handle_spending(trans_date, curr)
        elif op == transaction.Operation.GIFT_SENT:
            return _handle_gift_sent(trans_date, curr)
        elif op == transaction.Operation.SELL:
            return _make_adhoc_sell(trans_date, curr)
        elif op == transaction.Operation.BUY:
            return _handle_buy(trans_date, curr)
        else:
            # Should be unreachable as we checked if we did not match above.
            assert False

    def __iter__(self):
        return self


def _read_usd_value(usd_str):
    # type: (str) -> decimal.Decimal
    """
    Accept '$10,000.00' '$10,000' or '10000' or ''
    """
    if not usd_str:
        return None
    usd_str = usd_str.lstrip("$")
    usd_str = usd_str.replace(",", "")
    if not usd_str:
        return decimal.Decimal(0)
    return decimal.Decimal(usd_str)


def _handle_spending(date, curr):
    # type: (datetime.datetime, dict) -> transaction.Transaction
    cost_basis = 0
    fees = 0
    fee_coin = "USD"
    if curr[_RECEIVED_AMOUNT]:
        cost_basis = _read_usd_value(curr[_RECEIVED_AMOUNT])
    if curr[_FEE]:
        fees = curr[_FEE]
        fee_coin = curr[_FEE_COIN]

    return transaction.Transaction(
        transaction.Operation.SPENDING,
        date=date,
        symbol_traded=curr[_TRADED_CURRENCY],
        quantity_traded=decimal.Decimal(curr[_TRADED_AMOUNT]),
        quantity_received=cost_basis,
        symbol_received="USD",
        fees=fees,
        fee_symbol=fee_coin,
        source=AdhocParser.exchange_id_str(),
    )


def _handle_buy(date, curr):
    # type: (datetime.datetime, dict) -> transaction.Transaction
    fees = 0
    feecoin = "USD"
    if curr[_FEE]:
        fees = curr[_FEE]
        feecoin = curr[_FEE_COIN]
    return transaction.Transaction(
        transaction.Operation.BUY,
        date=date,
        symbol_traded="USD",
        quantity_traded=curr[_TRADED_AMOUNT],
        symbol_received=curr[_RECEIVED_CURRENCY],
        quantity_received=curr[_RECEIVED_AMOUNT],
        fees=fees,
        fee_symbol=feecoin,
        source=AdhocParser.exchange_id_str(),
    )


def _handle_gift_received(date, curr):
    cost_basis = 0
    basis_currency = "USD"
    if curr[_TRADED_AMOUNT]:
        cost_basis = _read_usd_value(curr[_TRADED_AMOUNT])

    return transaction.Transaction(
        transaction.Operation.GIFT_RECEIVED,
        date=date,
        # Cost basis, optional
        symbol_traded=basis_currency,
        quantity_traded=cost_basis,
        # What was actually received
        quantity_received=curr[_RECEIVED_AMOUNT],
        symbol_received=curr[_RECEIVED_CURRENCY],
        source=AdhocParser.exchange_id_str(),
    )


def _handle_gift_sent(date, curr):
    return transaction.Transaction(
        transaction.Operation.GIFT_SENT,
        date=date,
        symbol_traded=curr[_TRADED_CURRENCY],
        quantity_traded=curr[_TRADED_AMOUNT],
        symbol_received="USD",
        quantity_received=0,
        source=AdhocParser.exchange_id_str(),
    )


def _handle_mining(date, curr):
    # type: (datetime.datetime, dict) -> transaction.Transaction
    # TODO: for mining we need to look up the value on the date mined.
    #       Optionally, the value can be specified
    mined_value = 0
    if curr[_TRADED_AMOUNT]:
        mined_value = _read_usd_value(curr[_TRADED_AMOUNT])

    trans = transaction.Transaction(
        operation=transaction.Operation.MINING,
        quantity_received=curr[_RECEIVED_AMOUNT],
        symbol_received=curr[_RECEIVED_CURRENCY],
        fees=0,
        symbol_traded="USD",
        quantity_traded=mined_value,
        date=date,
        source=AdhocParser.exchange_id_str(),
    )
    return trans


def _make_adhoc_sell(date, curr):
    if curr[_RECEIVED_CURRENCY]:
        fee = 0
        fee_coin = "USD"
        rcvd_coin = curr[_RECEIVED_CURRENCY]
        rcvd_amount = curr[_RECEIVED_AMOUNT]
        if not rcvd_amount or not rcvd_coin:
            raise RuntimeError(
                "Invalid row, need currency and amount if either is specified {}".format(
                    curr
                )
            )
        if curr[_FEE]:
            fee = decimal.Decimal(curr[_FEE])
            fee_coin = curr[_FEE_COIN]
        return transaction.Transaction(
            transaction.Operation.SELL,
            symbol_received=rcvd_coin,
            quantity_received=decimal.Decimal(rcvd_amount),
            symbol_traded=curr[_TRADED_CURRENCY],
            quantity_traded=curr[_TRADED_AMOUNT],
            date=date,
            fees=fee,
            fee_symbol=fee_coin,
            source=AdhocParser.exchange_id_str(),
        )


FORMAT_CLASSES.append(AdhocParser)
