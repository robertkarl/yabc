#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.

import unittest

from yabc.formats import gemini

class GeminiCsvTest(unittest.TestCase):
    def test_load_from_csv(self):
        stuff = list(gemini.GeminiParser('./testdata/gemini/gemini.csv'))
        self.assertEqual(len(stuff), 2)
