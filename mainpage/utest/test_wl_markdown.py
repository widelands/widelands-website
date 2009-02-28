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
import sys; sys.path.append("..")

import unittest

from templatetags.wl_markdown import do_wl_markdown

class _TestWlMarkdown_Base(unittest.TestCase):
    def setUp(self):
        self.res = do_wl_markdown(self.input)

class TestWlMarkdown_SimpleCase_ExceptCorrectResult(_TestWlMarkdown_Base):
    input = u"Hallo Welt"
    wanted = u"<p>Hallo Welt</p>\n"
    def runTest(self):
        self.assertEqual(self.wanted,self.res)
# WlMarkup doesn't do urlization
# class TestWlMarkdown_AutoLinkHTTP_ExceptCorrectResult(_TestWlMarkdown_Base):
#     input = u"Sun: http://www.sun.com"
#     wanted = u"""<p>Sun: <a href="http://www.sun.com">http://www.sun.com</a></p>\n"""
#     def runTest(self):
#         self.assertEqual(self.wanted,self.res)
class TestWlMarkdown_WikiWordsSimple_ExceptCorrectResult(_TestWlMarkdown_Base):
    input = u"Na Du HalloWelt, Du?"
    wanted = u"""<p>Na Du <a href="/wiki/HalloWelt">HalloWelt</a>, Du?</p>\n"""
    def runTest(self):
        self.assertEqual(self.wanted,self.res)
class TestWlMarkdown_WikiWordsAvoid_ExceptCorrectResult(_TestWlMarkdown_Base):
    input = u"Hi !NotAWikiWord Moretext"
    wanted = u"""<p>Hi NotAWikiWord Moretext</p>\n"""
    def runTest(self):
        self.assertEqual(self.wanted,self.res)
class TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult(_TestWlMarkdown_Base):
    input = u"""WikiWord [NoWikiWord](http://www.sun.com)"""
    wanted = u"""<p><a href="/wiki/WikiWord">WikiWord</a> <a href="http://www.sun.com">NoWikiWord</a></p>\n"""
    def runTest(self):
        self.assertEqual(self.wanted,self.res)


if __name__ == '__main__':
    unittest.main()
    # k = TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult()
    # unittest.TextTestRunner().run(k)

