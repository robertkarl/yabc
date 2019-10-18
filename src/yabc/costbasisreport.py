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
from sqlalchemy import orm

import yabc
from yabc import transaction
from yabc.transaction import PreciseDecimalString


class CostBasisReport(yabc.Base):
    """
    Represents a row in form 8949.
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
    secondary_asset = Column(sqlalchemy.String)  # Needed for coin/coin trades.

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
        triggering_transaction=None,
        secondary_asset=None,
    ):
        # type: (int, decimal.Decimal, decimal.Decimal, datetime.datetime, decimal.Decimal, datetime.datetime, str, decimal.Decimal, transaction.Transaction) -> None
        """
        Note that when pulling items from a SQL alchemy ORM query, this constructor isn't called.
        """
        assert isinstance(date_sold, datetime.datetime)
        assert isinstance(date_purchased, datetime.datetime)
        assert isinstance(asset, str)
        self._round_to_dollar = True
        self.user_id = userid
        self.basis = self._round_as_needed(basis)
        self.quantity = quantity
        self.date_purchased = date_purchased
        self.proceeds = self._round_as_needed(proceeds)
        self.date_sold = date_sold
        self.asset_name = asset
        self.adjustment = adjustment
        self.long_term = self._is_long_term()
        self.triggering_transaction = triggering_transaction
        self.secondary_asset = secondary_asset

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
        return self._round_as_needed(self.proceeds - self.basis)

    def _round_as_needed(self, amount: decimal.Decimal):
        if self._round_to_dollar:
            return amount.quantize(1)
        return amount.quantize(Decimal(".01"))

    def description(self):
        """
        A description suitable for form 8949.

        For example, .06 BTC to USD
        """
        return "{:.6f} {} {}".format(
            self.quantity,
            self.asset_name,
            "to USD"
            if not self.secondary_asset
            else "to {}".format(self.secondary_asset),
        )

    def __repr__(self):
        return "<CostBasisReport: Sold {} {} on {date} for ${}. Exchange: {exchange}. Profit:${profit}.{longterm}\n\t{trigger}>".format(
            self.quantity,
            self.asset_name,
            self.proceeds,
            profit=self.gain_or_loss,
            date=self.date_sold,
            longterm=" Long term." if self.long_term else "",
            exchange=self.triggering_transaction.source
            if self.triggering_transaction
            else "Unknown",
            trigger=self.triggering_transaction,
        )

    def fields(self):
        ans = []
        for i in CostBasisReport._fields:
            ans.append(getattr(self, i))
        return ans

    @staticmethod
    def field_names():
        return CostBasisReport._fields

    @orm.reconstructor
    def init_on_load(self):
        self._round_to_dollar = True


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

    def totals(self):
        """
        :return:  dict with keys ["proceeds", "basis", "adjustment", "gain_or_loss"]
        """
        if not self._totals:
            self._totals = defaultdict(decimal.Decimal)
            for r in self.reports:
                for key in self.KEYS:
                    self._totals[key] += getattr(r, key)
        return self._totals

    def human_readable_report(self):
        """
        Given a list of CostBasisReports to be submitted to tax authorities, generate a human
        readable report.

        :return str:
        """
        ans = ""
        ans += "{} transactions to be reported\n\n".format(len(self.reports))
        for i in self.reports:
            ans += "{}\n".format(str(i))
        ans += "\ntotal gain or loss for above transactions: {}".format(
            self.totals()["gain_or_loss"]
        )
        ans += "\n"
        ans += "\ntotal basis for above transactions: {}".format(self.totals()["basis"])
        ans += "\ntotal proceeds for above transactions: {}".format(
            self.totals()["proceeds"]
        )
        return ans
