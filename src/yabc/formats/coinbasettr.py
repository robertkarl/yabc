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

TIMESTAMP_HEADER = "Timestamp"
TRANSACTION_TYPE_HEADER = "Transaction Type"
ASSET_HEADER = "Asset"
QUANTITY_TRANSACTED_HEADER = "Quantity Transacted"
USD_SPOT_PRICE_HEADER = "USD Spot Price at Transaction"
SUBTOTAL_HEADER = "Subtotal"
TOTAL_HEADER = "Total (Inclusive of fees)"

_ALL_HEADERS = [
    TIMESTAMP_HEADER,
    TRANSACTION_TYPE_HEADER,
    ASSET_HEADER,
    QUANTITY_TRANSACTED_HEADER,
    USD_SPOT_PRICE_HEADER,
    SUBTOTAL_HEADER,
    TOTAL_HEADER,
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
            kind = line[TRANSACTION_TYPE_HEADER]
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
            quantity = decimal.Decimal(line[QUANTITY_TRANSACTED_HEADER])
            fiat = decimal.Decimal(line[TOTAL_HEADER].rstrip(' USD').replace(',', ''))
            spot_price = decimal.Decimal(line[USD_SPOT_PRICE_HEADER])
            fiat_fee = fiat - (spot_price * quantity)
            if tx_type == transaction.Operation.SELL:
                fiat_fee *= -1
            if fiat_fee < 0:
                # This can happen for small transactions
                fiat_fee = decimal.Decimal(0)
            return transaction.Transaction(
                operation=tx_type,
                asset_name=asset_name,
                date=date,
                fees=fiat_fee,
                quantity=quantity,
                source=self.exchange_id_str(),
                usd_subtotal=fiat - fiat_fee,
            )
        except decimal.DecimalException as e:
            raise RuntimeError("Could not parse Coinbase TTR decimal.")
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
        header_checked = False
        for line in self._reader:
            if not header_checked:
                if 'Coinbase' not in line['Timestamp']:
                    # The first line has a disclaimer which contains the word Coinbase
                    raise RuntimeError("Not a Coinbase TTR")
                header_checked = True
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
