import datetime

import delorean

jan_1 = datetime.datetime(2017, 1, 1).date()
_ETH_DATA = {jan_1: 8}
_BTC_DATA = {jan_1: 1000}
_PRICE_DATA = {"ETH": _ETH_DATA, "BTC": _BTC_DATA}


def historical(date: datetime.date, coin):
    """
    Perform an API call to get the price of an asset at a given timestamp.

    For testing, returns some sample data.

    TODO: provide better test data.

    :param date:
    :param coin:
    :return:
    """
    if isinstance(date, (datetime.datetime, delorean.Delorean)):
        date = date.date
    try:
        val = _PRICE_DATA[coin][date]
        return val
    except Exception as e:
        return 17
