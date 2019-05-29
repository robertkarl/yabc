import doctest

import yabc


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(yabc.basis))
    return tests
