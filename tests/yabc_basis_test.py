import doctest
import unittest

import yabc


class YabcBasisTest(unittest.TestCase):
    def test_docs(self):
        doctest.testmod(yabc.basis)
