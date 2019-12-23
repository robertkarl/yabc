"""
The Coinbase Tax Transactions Report format.

YABC is not affiliated with the company Coinbase or any of its products.

003 = {list: 8} ['Timestamp', 'Transaction Type', 'Asset', 'Quantity Transacted', 'USD Spot Price at Transaction', 'USD Amount Transacted (Inclusive of Coinbase Fees)', 'Address', 'Notes']
004 = {list: 8} ['10/06/2015', 'Buy', 'BTC', '1.0', '247.26', '249.73', '', 'Bought 1.0000 BTC for $249.73 USD.\n\nPaid for with Bank Name. Your BTC will arrive by the end of day on Tuesday Oct 13, 2015.']
"""
import csv
import datetime
import decimal

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format

_TIMESTAMP_HEADER = "Timestamp"
_TRANSACTION_TYPE_HEADER = "Transaction Type"
_FIAT_TRANSACTED_HEADER = "USD Amount Transacted (Inclusive of Coinbase Fees)"
_QUANTITY_TRANSACTED_HEADER = "Quantity Transacted"
_SPOT_PRICE_HEADER = "USD Spot Price at Transaction"
_ASSET_HEADER = "Asset"

_ALL_HEADERS = [
    _TIMESTAMP_HEADER,
    _TRANSACTION_TYPE_HEADER,
    _ASSET_HEADER,
    _QUANTITY_TRANSACTED_HEADER,
    _SPOT_PRICE_HEADER,
    _FIAT_TRANSACTED_HEADER,
    "Address",
    "Notes",
]


class CoinbaseTTRParser(Format):
    FORMAT_NAME = "Coinbase (Tax Transaction Report Format)"
    EXCHANGE_HUMAN_READABLE_NAME = "Coinbase"
    _EXCHANGE_ID_STR = "coinbase"

    def attempt_read_transaction(self, line):
        """
        Return None if the row is not taxable.
        """
        try:
            kind = line[_TRANSACTION_TYPE_HEADER]
            if kind == "Buy":
                tx_type = transaction.Transaction.Operation.BUY
            elif kind == "Sell":
                tx_type = transaction.Transaction.Operation.SELL
            else:
                return None
            date = delorean.parse(line["Timestamp"], dayfirst=False).datetime
            if date == self._last_date:
                date += self._trade_time_delta
            self._last_date = date

            asset_name = line["Asset"]
            quantity = decimal.Decimal(line[_QUANTITY_TRANSACTED_HEADER])
            fiat = decimal.Decimal(line[_FIAT_TRANSACTED_HEADER])
            spot_price = decimal.Decimal(line[_SPOT_PRICE_HEADER])
            fiat_fee = fiat - (spot_price * quantity)
            if tx_type == transaction.Operation.SELL:
                fiat_fee *= -1
            assert fiat_fee >= 0
            return transaction.Transaction(
                operation=tx_type,
                asset_name=asset_name,
                date=date,
                fees=fiat_fee,
                quantity=quantity,
                source=self.exchange_id_str(),
                usd_subtotal=fiat - fiat_fee,
            )
        except RuntimeError:
            raise RuntimeError("Could not parse Coinbase TTR data.")
        except KeyError as e:
            raise RuntimeError("Unknown key in CoinbaseTTR file: {}".format(e))

    def __init__(self, csv_content=None, filename=None):
        self._last_date = None
        self._trade_time_delta = datetime.timedelta(seconds=1)
        if csv_content:
            assert not filename
            csv_content.seek(0)
            self._file = csv_content
            self._reader = csv.DictReader(csv_content, fieldnames=_ALL_HEADERS)
        else:
            assert not csv_content
            self._file = open(filename, "r")
            self._reader = csv.DictReader(self._file, fieldnames=_ALL_HEADERS)
        self.txs = []
        for line in self._reader:
            tx = self.attempt_read_transaction(line)
            if tx is not None:
                self.txs.append(tx)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)

    def cleanup(self):
        try:
            self._file.close()
        except:
            pass


FORMAT_CLASSES.append(CoinbaseTTRParser)
