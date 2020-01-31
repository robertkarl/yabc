import unittest

from transaction_utils import make_transaction
from yabc import coinpool
from yabc.basis import BasisProcessor
from yabc.transaction import *
import doctest
from yabc import costbasisreport


class CostBasisReportDocTests(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_module(self):
        doctest.testmod(costbasisreport)
