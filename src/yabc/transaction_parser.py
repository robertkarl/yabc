import collections
from typing import Sequence

import yabc

TxFile = collections.namedtuple('InputFile', ('file', 'parser_hint'))

import yabc.formats

class TransactionParser:
    """
    Turn collections of file-like objects into a transaction list.
    """
    def __init__(self, files: Sequence[TxFile]):
        self.txs = []
        for f, hinted_parser in files:
            self.txs.extend(self._get_txs(f, hinted_parser))
        self.flags = []

    def _get_txs(self, f, hinted_parser):
        if hinted_parser is not None:
            return list(hinted_parser(f))
        # Try formats until something works.
        for constructor in yabc.formats.format_classes:
            try:
                generator = constructor(f)
                values = list(generator)
                return values
            except RuntimeError:
                continue
        self.flags.append("WARNING: couldn't find any transactions in file {}".format(f))
        return []
