#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
from collections import namedtuple

import delorean
import datetime
import decimal

OhlcData = namedtuple('OhlcData', ('open', 'high', 'low', 'close'))

jan_1 = datetime.datetime(2017, 1, 1).date()
_ETH_DATA = {jan_1: OhlcData(*[decimal.Decimal(i) for i in ['8.5', '8.6', '8.0', '8.1']])}
_ETH_DATA = {jan_1: OhlcData(*[decimal.Decimal(i) for i in ['1000', '1008.6', '990', '1000']])}
_BTC_DATA = {jan_1: 1000}
_PRICE_DATA = {"ETH": _ETH_DATA, "BTC": _BTC_DATA}


class OhlcProvider:
    """
    Daily OHLC data access stub.
    """

    def __init__(self):
        pass

    def get(self, symbol, dt):
        # type: (str, datetime.datetime) -> OhlcData
        """
        Return the price in USD.
        """
        if isinstance(dt, (datetime.datetime, delorean.Delorean)):
            date = dt.date
        try:
            val = _PRICE_DATA[symbol][date]
            return val
        except Exception as e:
            return 17

