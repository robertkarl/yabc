import csv
import decimal
import enum

import delorean

from yabc import transaction
from yabc.formats import FORMAT_CLASSES
from yabc.formats import Format
from yabc.transaction import Operation


"""
TXID, Created, Received, Sent, TXtype, TXdesc, TXNotes
,2015-04-05T02:03:47+00:00,1.50000000,,Deposit,
"""


class LocalBitcoinTradeTypes(enum.Enum):
    # Sales (for tax purposes)
    LOCAL_SELL = "LOCAL_SELL"
    ONLINE_BUY = "ONLINE_BUY"
    # Purchasing bitcoin (for tax purposes)
    ONLINE_SELL = "ONLINE_SELL"
    LOCAL_BUY = "LOCAL_BUY"


def _is_sell(trade_type: LocalBitcoinTradeTypes):
    return trade_type in {
        LocalBitcoinTradeTypes.LOCAL_SELL,
        LocalBitcoinTradeTypes.ONLINE_BUY,
    }


class LocalBitcoinsParser(Format):
    _EXCHANGE_ID_STR = "localbitcoins"
    EXCHANGE_HUMAN_READABLE_NAME = "LocalBitcoins.com"

    def attempt_read_transaction(self, line):
        try:
            kind = LocalBitcoinTradeTypes[line["trade_type"]]
            date = delorean.parse(
                line["transaction_released_at"], dayfirst=False
            ).datetime
            btc_amount = line["btc_traded"]
            fiat = decimal.Decimal(line["fiat_amount"])
            fiat_fee = decimal.Decimal(line["fiat_fee"])
            if _is_sell(kind):
                tx_type = Operation.SELL
            else:
                tx_type = Operation.BUY
            return transaction.Transaction(
                operation=tx_type,
                asset_name="BTC",
                date=date,
                fees=fiat_fee,
                quantity=btc_amount,
                source=LocalBitcoinsParser.exchange_id_str(),
                usd_subtotal=fiat,
            )
        except RuntimeError:
            raise RuntimeError("Could not parse localbitcoins data.")
        except KeyError as e:
            raise RuntimeError("Unknown key in localbitcoins file: {}".format(e))

    def __init__(self, csv_content=None, filename=None):
        if csv_content:
            assert not filename
            csv_content.seek(0)
            self._file = csv_content
            self._reader = csv.DictReader(csv_content)
        else:
            assert not csv_content
            self._file = open(filename, "r")
            self._reader = csv.DictReader(self._file)
        self.txs = []
        for line in self._reader:
            tx = self.attempt_read_transaction(line)
            self.txs.append(tx)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)


FORMAT_CLASSES.append(LocalBitcoinsParser)
