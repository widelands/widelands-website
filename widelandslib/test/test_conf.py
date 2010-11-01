#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: test_macro.py
#
# Created by Holger Rapp on 18.01.09  
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

import sys
sys.path.append("..")

import unittest
from cStringIO import StringIO

from conf import WidelandsConfigParser

class _WLConfigParser_Base( unittest.TestCase ):
    def setUp(self):
        self.cp = WidelandsConfigParser( StringIO(self.input ))
        
class TestWLConfigParser_TestStringSubstitution_ExceptCorrectResult(_WLConfigParser_Base):
    # {{{ Data
    input="""[global]
descr=_"The breath-taking beauty of these emerald lands has lured many a tribe into the attempt of taking them for itself."
"""
    wanted = "The breath-taking beauty of these emerald lands has lured many a tribe into the attempt of taking them for itself."
    # }}}
    def runTest(self):
        self.assertEqual( self.cp.getstring("global","descr"), self.wanted )


if __name__ == '__main__':
    unittest.main()
    # k = TestMacro_UnmatchedExitm_ExceptRaise()
    # unittest.TextTestRunner().run(k)

