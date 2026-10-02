#!/usr/bin/python -tt

import hashlib
import unittest
import datetime
from unittest import mock

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.models import User
from django.test import TestCase

from .hashers import wrap_legacy_sha1_hashes
from .templatetags.custom_date import do_custom_date


class _CustomDate_Base(unittest.TestCase):
    def setUp(self):
        self.date = datetime.datetime(2008, 4, 12, 12, 53, 21)


class TestCustomDate_PythonReplacement_ExceptCorrectResult(_CustomDate_Base):
    def runTest(self):
        rv = do_custom_date("r", self.date, 2)
        self.assertEqual("Sat, 12 Apr 2008 13:53:21 +0200", rv)


class TestCustomDate_PythonReplacement2_ExceptCorrectResult(_CustomDate_Base):
    def runTest(self):
        rv = do_custom_date("j.m.Y", self.date, 0)
        self.assertEqual("12.04.2008", rv)


class TestCustomDate_NaturalYearReplacementSame_ExceptCorrectResult(_CustomDate_Base):
    def runTest(self):
        now = datetime.datetime(2008, 4, 12, 12, 53, 21)
        rv = do_custom_date("m%NY(.Y)", self.date, 0, now)
        self.assertEqual("04", rv)


class TestCustomDate_NaturalYearReplacementDifferent_ExceptCorrectResult(
    _CustomDate_Base
):
    def runTest(self):
        now = datetime.datetime(2009, 4, 12, 12, 53, 21)
        rv = do_custom_date("m%NY(.Y)", self.date, 0, now)
        self.assertEqual("04.2008", rv)


class TestCustomDate_NaturalYearReplacementTwice_ExceptCorrectResult(_CustomDate_Base):
    def runTest(self):
        now = datetime.datetime(2009, 4, 12, 12, 53, 21)
        rv = do_custom_date(r"m%NY(.Y) \b\l\a\h \m\o\r\e %NY(m.Y)", self.date, 0, now)
        self.assertEqual("04.2008 blah more 04.2008", rv)


class TestCustomDate_NaturalDayReplacementToday_ExceptCorrectResult(_CustomDate_Base):
    def runTest(self):
        now = datetime.datetime(2008, 4, 12, 0, 0, 21)
        rv = do_custom_date("j.m.y: %ND(j.m.y)", self.date, 0, now)
        self.assertEqual("12.04.08: Today", rv)


class TestCustomDate_NaturalDayReplacementTomorrow_ExceptCorrectResult(
    _CustomDate_Base
):
    def runTest(self):
        now = datetime.datetime(2008, 4, 11, 23, 59, 59)
        rv = do_custom_date("j.m.y: %ND(j.m.y)", self.date, 0, now)
        self.assertEqual("12.04.08: Tomorrow", rv)


class TestCustomDate_NaturalDayReplacementYesterday_ExceptCorrectResult(
    _CustomDate_Base
):
    def runTest(self):
        now = datetime.datetime(2008, 4, 13, 00, 00, 0o1)
        rv = do_custom_date("j.m.y: %ND(j.m.y)", self.date, 0, now)
        self.assertEqual("12.04.08: Yesterday", rv)


class TestCustomDate_NaturalDayReplacementNoSpecialDay_ExceptCorrectResult(
    _CustomDate_Base
):
    def runTest(self):
        now = datetime.datetime(2011, 4, 13, 00, 00, 0o1)
        rv = do_custom_date("j.m.y: %ND(j.m.Y)", self.date, 0, now)
        self.assertEqual("12.04.08: 12.04.2008", rv)


class TestCustomDate_RecursiveReplacementNoHit_ExceptCorrectResult(_CustomDate_Base):
    def runTest(self):
        now = datetime.datetime(2011, 4, 13, 00, 00, 0o1)
        rv = do_custom_date("j.m.y%ND(: j.m%NY(.Y))", self.date, 0, now)
        self.assertEqual("12.04.08: 12.04.2008", rv)


class TestCustomDate_RecursiveReplacementMissDayHitYear_ExceptCorrectResult(
    _CustomDate_Base
):
    def runTest(self):
        now = datetime.datetime(2008, 9, 13, 00, 00, 0o1)
        rv = do_custom_date("j.m.y: %ND(j.m.%NY(Y))", self.date, 0, now)
        self.assertEqual("12.04.08: 12.04.", rv)


class TestCustomDate_RecursiveReplacementHitDayTodayHitYear_ExceptCorrectResult(
    _CustomDate_Base
):
    def runTest(self):
        now = datetime.datetime(2008, 4, 12, 00, 00, 0o1)
        rv = do_custom_date("j.m.y: %ND(j.m.%NY(Y))", self.date, 0, now)
        self.assertEqual("12.04.08: Today", rv)


#########
# FAILS #
#########
class TestCustomDate_FaultyDate_ExceptNoop(unittest.TestCase):
    def runTest(self):
        rv = do_custom_date("%c", (93, 93), 0)
        self.assertEqual("%c", rv)


class TestLegacySha1Passwords(TestCase):
    def setUp(self):
        # Keep PBKDF2 cheap; production uses Django's default iterations.
        patcher = mock.patch.object(PBKDF2PasswordHasher, "iterations", 1000)
        patcher.start()
        self.addCleanup(patcher.stop)
        digest = hashlib.sha1(b"saltsecret").hexdigest()
        self.user = User.objects.create(username="old", password=f"sha1$salt${digest}")
        wrap_legacy_sha1_hashes(User)
        self.user.refresh_from_db()

    def test_wrapped_hash_replaces_sha1(self):
        self.assertTrue(self.user.password.startswith("pbkdf2_wrapped_sha1$"))

    def test_wrong_password_rejected(self):
        self.assertIsNone(authenticate(username="old", password="wrong"))

    def test_login_works_and_upgrades_to_default_hasher(self):
        self.assertEqual(self.user, authenticate(username="old", password="secret"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.password.startswith("pbkdf2_sha256$"))
        self.assertEqual(self.user, authenticate(username="old", password="secret"))


if __name__ == "__main__":
    unittest.main()
