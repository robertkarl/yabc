"""
Definition of a Transaction, the in-memory version of an asset buy/sell
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import datetime

import dateutil
import sqlalchemy
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import sessionmaker

import yabc


class Transaction(yabc.Base):
    """
    Exchange-independent representation of a transaction (buy or sell)
    """

    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)
    asset_name = Column(String)
    btc_quantity = Column(Float)
    date = Column(DateTime)
    operation = Column(String)
    source = Column(String)
    source = Column(String)
    usd_btc_price = Column(Float)

    def __init__(
        self,
        operation=None,
        btc_quantity=0,
        date=None,
        usd_bitcoin_price=0,
        source=None,
        asset_name="BTC",
    ):
        assert operation in ["Buy", "Sell"]
        assert date is not None
        assert type(btc_quantity) is float
        assert btc_quantity > 0
        self.btc_quantity = btc_quantity
        self.operation = operation
        self.date = date.replace(tzinfo=None)
        self.usd_btc_price = usd_bitcoin_price
        self.source = source
        self.asset_name = "BTC"

    @staticmethod
    def FromCoinbaseJSON(json):
        """
        Arguments:
            json (dict): a coinbase-style dictionary with the following fields:
                - 'Transfer Total': the total price, including fees.
                - 'Transfer Fee': the fee charged by the exchange.
                - 'Amount': the amount of bitcoin sold. (It's negative for
                  sales.)
                - 'Timestamp': 'hour:min:sec.millisecs' formatted timestamp.
        Returns: Transaction instance with important fields populated
        """
        operation = "Buy"
        total_price = float(json["Transfer Total"])
        fee = float(json["Transfer Fee"])
        btc_quantity = float(json["Amount"])
        if btc_quantity < 0:
            operation = "Sell"
            btc_quantity = abs(btc_quantity)
        assert btc_quantity > 0
        unit_price = (total_price - fee) / btc_quantity
        timestamp_str = json["Timestamp"]
        # TODO(robertkarl): I assume we're only supporting USD <-> BC
        # transactions?
        return Transaction(
            operation,
            btc_quantity=btc_quantity,
            date=dateutil.parser.parse(timestamp_str),
            source="coinbase",
            usd_bitcoin_price=unit_price,
        )

    @staticmethod
    def FromGeminiJSON(json):
        """
        Arguments
            json (Dictionary): 
        """
        operation = json["Type"]
        btc_quantity = float(json["BTC Amount"])
        usd_total = float(json["USD Amount"])
        fee = float(json["USD Fee"])
        assert fee >= 0  # Fee can round to zero for small trannies
        unit_price = float(usd_total) / btc_quantity
        assert unit_price > 0
        timestamp_str = "{}".format(json["Date"])
        # TODO(robertkarl): the original format seems to only include the date.
        # The timestamp needs the time as well (e.g. we should use the below
        # line). For now, I'm focusing on making a small PR to add basic tests,
        # so punting for now.
        # timestamp_str = "{} {}".format(json['Date'], json['Time'])

        return Transaction(
            operation,
            btc_quantity=btc_quantity,
            date=dateutil.parser.parse(timestamp_str),
            source="gemini",
            usd_bitcoin_price=unit_price,
        )

    def __repr__(self):
        return "<TX: {} {} BTC @ {}, on {} from exchange {}>".format(
            self.operation,
            self.btc_quantity,
            self.usd_btc_price,
            self.date,
            self.source,
        )
