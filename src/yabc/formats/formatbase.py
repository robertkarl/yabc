# Copyright (c) Seattle Blockchain Solutions. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
import logging


class Format:
    """
    Base class for formats from various exchanges.
    """

    FORMAT_NAME = "Unknown exchange - CSV"
    EXCHANGE_HUMAN_READABLE_NAME = "Unknown exchange"
    _EXCHANGE_ID_STR = "unknown"

    @classmethod
    def exchange_id_str(cls):
        """
        Machine-friendly string ID of this exchange.
        :return: str
        """
        return cls._EXCHANGE_ID_STR

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
