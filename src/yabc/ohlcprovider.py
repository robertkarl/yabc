#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime
import decimal
from collections import namedtuple

OhlcData = namedtuple("OhlcData", ("open", "high", "low", "close"))


def _make_ohlc(ohlc_str):
    # type: (str) -> OhlcData
    return OhlcData(*[decimal.Decimal(i) for i in ohlc_str.split()])


def _make_date(date_str):
    return datetime.datetime(*[int(i) for i in date_str.split()]).date()


jan_1 = datetime.datetime(2017, 1, 1).date()
_ETH_DATA = {
    jan_1: _make_ohlc("8.5 8.6 8.0 8.1"),
    _make_date("2018 5 22"): _make_ohlc("700 701 644 648"),
    _make_date("2019 4 16"): _make_ohlc("162 168 161 168"),
}
_BTC_DATA = {
    jan_1: _make_ohlc("1000 1008.6 990 1000"),
    _make_date("2018 5 22"): _make_ohlc("8420 8423 8005 8042"),
    _make_date("2019 4 16"): _make_ohlc("5066 5238 5055 5235"),
}
_PRICE_DATA = {"ETH": _ETH_DATA, "BTC": _BTC_DATA}


class NoDataError(RuntimeError):
    pass


class OhlcProvider:
    """
    Daily OHLC data access stub.
    """

    def __init__(self):
        pass

    def get(self, symbol, dt):
        # type: (str, datetime.datetime) -> OhlcData
        """
        Return the fiat OHLC prices.
        """
        if isinstance(dt, (datetime.datetime)):
            dt = dt.date()
        try:
            val = _PRICE_DATA[symbol][dt]
            return val
        except KeyError:
            raise NoDataError("No price data found for {} on {}.".format(symbol, dt))
