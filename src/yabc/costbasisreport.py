import datetime
import decimal
from collections import defaultdict
from decimal import Decimal

import sqlalchemy
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

import yabc
from yabc.transaction import PreciseDecimalString


def round_to_dollar(dec: decimal.Decimal):
    return dec.quantize(1)


def round_to_dollar_str(dec):
    """
    Convert an arbitrary precision decimal object to a string rounded to the
    NEAREST dollar.

    >>> round_to_dollar_str(decimal.Decimal("1.500001"))
    '2.'
    >>> round_to_dollar_str(decimal.Decimal("1.499999"))
    '1.'
    >>> round_to_dollar_str(decimal.Decimal("-1.499999"))
    '-1.'
    """
    return "{:.0f}.".format(round_to_dollar(dec))


class CostBasisReport(yabc.Base):
    """
    Represents a row in form 8949.
    TODO: Add wash sales.
    TODO: Check that long term results match expected in leap years.

    >>> r = CostBasisReport.make_random_report()
    >>> r.date_sold = datetime.datetime(2019,1,1)
    >>> r.date_purchased = datetime.datetime(2018,1,1)
    >>> r._is_long_term()
    True
    >>> r.date_purchased = datetime.datetime(2018,1,2)
    >>> r._is_long_term()
    False
    """

    _fields = [
        "id",
        "asset_name",
        "basis",
        "date_purchased",
        "date_sold",
        "proceeds",
        "quantity",
        "long_term",
        "adjustment",
        "user_id",
    ]

    __tablename__ = "basis_report"
    id = Column(Integer, primary_key=True)
    asset_name = Column(sqlalchemy.String)
    basis = Column(PreciseDecimalString)
    date_purchased = Column(DateTime)
    date_sold = Column(DateTime)
    proceeds = Column(PreciseDecimalString)
    quantity = Column(PreciseDecimalString)
    adjustment = Column(PreciseDecimalString)
    long_term = Column(Boolean)
    user_id = Column(sqlalchemy.Integer, ForeignKey("user.id"))

    @staticmethod
    def make_random_report():
        return CostBasisReport(
            1,
            Decimal(1),
            Decimal(1),
            datetime.datetime.now(),
            Decimal(2),
            datetime.datetime.now(),
            "BTC",
        )

    def __init__(
        self,
        userid,
        basis,
        quantity,
        date_purchased,
        proceeds,
        date_sold,
        asset,
        adjustment=Decimal(0),
    ):
        """
        Note that when pulling items from a SQL alchemy ORM query, this constructor isn't called.
        """
        assert isinstance(date_sold, datetime.datetime)
        assert isinstance(date_purchased, datetime.datetime)
        assert isinstance(asset, str)
        self.user_id = userid
        self.basis = basis
        self.quantity = quantity
        self.date_purchased = date_purchased
        self.proceeds = proceeds
        self.date_sold = date_sold
        self.asset_name = asset
        self.adjustment = adjustment
        self.long_term = self._is_long_term()

    def _is_long_term(self):
        return (self.date_sold - self.date_purchased) > datetime.timedelta(364)

    def __getattr__(self, item):
        if item == "gain_or_loss":
            return self.get_gain_or_loss(True)
        raise AttributeError()

    def get_gain_or_loss(self, round_dollars=True):
        """
        This field is calculated based on proceeds and basis.

        It could return different values based on different printings of a user's tax info.

        :param round_dollars: We only support True so far.
        :return:
        """
        proceeds = round_to_dollar(self.proceeds) if round_dollars else self.proceeds
        basis = round_to_dollar(self.basis) if round_dollars else self.basis
        return proceeds - basis

    def description(self):
        return "{:.6f} {}".format(self.quantity, self.asset_name)

    def __repr__(self):
        return "<Sold {} {} for {} total profiting {}>".format(
            self.quantity, self.asset_name, self.proceeds, self.gain_or_loss
        )

    def fields(self):
        ans = []
        for i in CostBasisReport._fields:
            ans.append(getattr(self, i))
        return ans

    @staticmethod
    def field_names():
        return CostBasisReport._fields


class ReportBatch:
    """
    Contain a list of reports and any context needed for calculating totals.

    8949 needs the total revenue, for example.

    Most notable is whether or not to round to the nearest dollar.

    >>> r1 = CostBasisReport.make_random_report()
    >>> r1.gain_or_loss = decimal.Decimal('1.5')
    >>> r2 = CostBasisReport.make_random_report()
    >>> r2.gain_or_loss = decimal.Decimal('1.5')
    >>> batch = ReportBatch([r1, r2], True)
    >>> batch.totals()['gain_or_loss'] == decimal.Decimal('4')
    True
    >>> batch_no_rounding = ReportBatch([r1, r2], False)
    >>> batch_no_rounding.totals()['gain_or_loss'] == decimal.Decimal('3')
    True
    """

    KEYS = ["proceeds", "basis", "adjustment", "gain_or_loss"]

    def __init__(self, reports, round_dollars=True):
        self.reports = reports
        self.round_dollars = round_dollars
        self._totals = None

    def _round_if_necessary(self, amount: decimal.Decimal):
        if self.round_dollars:
            return round_to_dollar(amount)
        return amount

    def totals(self):
        """
        :return:  dict with keys ["proceeds", "basis", "adjustment", "gain_or_loss"]
        """
        if not self._totals:
            self._totals = defaultdict(decimal.Decimal)
            for r in self.reports:
                for key in self.KEYS:
                    self._totals[key] += self._round_if_necessary(getattr(r, key))
        return self._totals
