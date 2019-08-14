# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
import logging


class Format:
    """
    Base class for formats from various exchanges.
    """

    EXCHANGE_NAME = "Unknown exchange"

    @classmethod
    def exchange_name(cls):
        """
        Human-friendly name of this exchange.
        :return: str
        """
        return cls.EXCHANGE_NAME

    def has_next(self):
        if not self._reports:
            return False
        return True

    def cleanup(self):
        logging.info("cleaning up file {}".format(self._file))
        if self._file:
            try:
                # self._file can be a sequence, which shouldn't have close().
                self._file.close()
            except AttributeError:
                pass
            del self._file


FORMAT_CLASSES = []


def add_supported_exchanges():
    """
    This is in a function mostly so our automated reformatting scripts don't place these imports above all statements

    #noqa should stop our unused import zapper from zapping.
    TODO: add binance. See comment in binance file.
    """
    from . import adhoc  # noqa
    from . import coinbase  # noqa
    from . import gemini  # noqa
    from . import localbitcoins  # noqa


add_supported_exchanges()
