#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: utests/test_wl_markdown.py
#
# Created by Holger Rapp on 2009-02-28.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

# Since we want to include something from one path up,
# we append the parent path to sys.path
import sys

sys.path.append("..")

import unittest

from models import Image


class TestImages_TestUploading_ExceptCorrectResult(unittest.TestCase):
    def runTest(self):
        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
    # k = TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult()
    # unittest.TextTestRunner().run(k)
