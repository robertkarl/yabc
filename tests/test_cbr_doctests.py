import doctest
import unittest

from yabc import costbasisreport


class CostBasisReportDocTests(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_module(self):
        doctest.testmod(costbasisreport)
