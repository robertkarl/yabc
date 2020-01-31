# Copyright (c) Robert Karl. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.

from . import formatbase

Format = formatbase.Format


FORMAT_CLASSES = []


def add_supported_exchanges():
    """
    TODO: these are circular imports; these files then attempt to import THIS file.
    """
    from . import adhoc  # noqa
    from . import binance  # noqa
    from . import bitmex  # noqa
    from . import bybit  # noqa
    from . import coinbase  # noqa
    from . import coinbasepro  # noqa
    from . import coinbasettr  # noqa
    from . import gemini  # noqa
    from . import localbitcoins  # noqa
