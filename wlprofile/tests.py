#!/usr/bin/python -tt

import unittest
import datetime

from .templatetags.custom_date import do_custom_date


class _CustomDate_Base(unittest.TestCase):

    def setUp(self):
        self.date = datetime.datetime(2008, 4, 12, 12, 53, 21)


class TestCustomDate_PythonReplacement_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        rv = do_custom_date('r', self.date, 2)
        self.assertEqual('Sat, 12 Apr 2008 13:53:21 +0200', rv)


class TestCustomDate_PythonReplacement2_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        rv = do_custom_date('j.m.Y', self.date, 0)
        self.assertEqual('12.04.2008', rv)


class TestCustomDate_NaturalYearReplacementSame_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2008, 4, 12, 12, 53, 21)
        rv = do_custom_date('m%NY(.Y)', self.date, 0, now)
        self.assertEqual('04', rv)


class TestCustomDate_NaturalYearReplacementDifferent_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2009, 4, 12, 12, 53, 21)
        rv = do_custom_date('m%NY(.Y)', self.date, 0, now)
        self.assertEqual('04.2008', rv)


class TestCustomDate_NaturalYearReplacementTwice_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2009, 4, 12, 12, 53, 21)
        rv = do_custom_date(
            r"m%NY(.Y) \b\l\a\h \m\o\r\e %NY(m.Y)", self.date, 0, now)
        self.assertEqual('04.2008 blah more 04.2008', rv)


class TestCustomDate_NaturalDayReplacementToday_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2008, 4, 12, 0, 0, 21)
        rv = do_custom_date('j.m.y: %ND(j.m.y)', self.date, 0, now)
        self.assertEqual('12.04.08: today', rv)


class TestCustomDate_NaturalDayReplacementTomorrow_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2008, 4, 11, 23, 59, 59)
        rv = do_custom_date('j.m.y: %ND(j.m.y)', self.date, 0, now)
        self.assertEqual('12.04.08: tomorrow', rv)


class TestCustomDate_NaturalDayReplacementYesterday_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2008, 4, 13, 00, 00, 0o1)
        rv = do_custom_date('j.m.y: %ND(j.m.y)', self.date, 0, now)
        self.assertEqual('12.04.08: yesterday', rv)


class TestCustomDate_NaturalDayReplacementNoSpecialDay_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2011, 4, 13, 00, 00, 0o1)
        rv = do_custom_date('j.m.y: %ND(j.m.Y)', self.date, 0, now)
        self.assertEqual('12.04.08: 12.04.2008', rv)


class TestCustomDate_RecursiveReplacementNoHit_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2011, 4, 13, 00, 00, 0o1)
        rv = do_custom_date('j.m.y%ND(: j.m%NY(.Y))', self.date, 0, now)
        self.assertEqual('12.04.08: 12.04.2008', rv)


class TestCustomDate_RecursiveReplacementMissDayHitYear_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2008, 9, 13, 00, 00, 0o1)
        rv = do_custom_date('j.m.y: %ND(j.m.%NY(Y))', self.date, 0, now)
        self.assertEqual('12.04.08: 12.04.', rv)


class TestCustomDate_RecursiveReplacementHitDayTodayHitYear_ExceptCorrectResult(_CustomDate_Base):

    def runTest(self):
        now = datetime.datetime(2008, 4, 12, 00, 00, 0o1)
        rv = do_custom_date('j.m.y: %ND(j.m.%NY(Y))', self.date, 0, now)
        self.assertEqual('12.04.08: today', rv)


#########
# FAILS #
#########
class TestCustomDate_FaultyDate_ExceptNoop(unittest.TestCase):

    def runTest(self):
        rv = do_custom_date('%c', (93, 93), 0)
        self.assertEqual('%c', rv)

if __name__ == '__main__':
    unittest.main()
