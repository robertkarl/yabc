import collections
import logging
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
        self.txs = []
        self.flags = []
        self.files = files
        self.parse()

    def _get_txs(self, f, hinted_parser):
        if hinted_parser is not None:
            return list(hinted_parser(f))
        # Try formats until something works.
        for constructor in yabc.formats.FORMAT_CLASSES:
            try:
                generator = constructor(f)
                values = list(generator)
                return values
            except RuntimeError as e:
                logging.info(e)
                continue
        self.flags.append(
            "ERROR: couldn't find any transactions in file {}".format(f)
        )
        return []
