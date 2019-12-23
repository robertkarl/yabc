import collections
from typing import Sequence

import yabc
import yabc.formats

TxFile = collections.namedtuple("InputFile", ("file", "parser_hint"))


class TransactionParser:
    """
    Turn collections of file-like objects into a transaction list.
    """

    def parse(self):
        for f, hinted_parser in self.files:
            self.txs.extend(self._get_txs(f, hinted_parser))

    def __init__(self, files: Sequence[TxFile]):
        """

        :param files: a sequence of TxFile objects.
        """
        self.txs = []
        self.flags = []
        self.files = files
        self._exchange = None
        self._success = False

    def get_exchange_name(self):
        if not self._exchange:
            return yabc.formats.formatbase.Format.exchange_id_str()
        return self._exchange.exchange_id_str()

    def succeeded(self):
        return self._success

    def _get_txs(self, f, hinted_parser):
        if hinted_parser is not None:
            return list(hinted_parser(f))
        # Try formats until something works.
        for constructor in yabc.formats.FORMAT_CLASSES:
            try:
                f.seek(0)
                generator = constructor(f)
                values = list(generator)
                self._exchange = constructor
                self._success = True
                return values
            except Exception:
                continue
        self._success = False
        self.flags.append("Couldn't find any transactions in file.")
        return []
