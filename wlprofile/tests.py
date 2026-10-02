#!/usr/bin/python -tt

import hashlib
import unittest
import datetime
from io import BytesIO
from unittest import mock

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .forms import EditProfileForm
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


class TestStateChangingViewsRequirePost(TestCase):
    def setUp(self):
        from notification.models import NoticeType, observe
        from pybb.models import Category, Forum, Topic
        from .models import Profile

        self.user = User.objects.create_user("alice", "alice@example.com", "pw")
        Profile.objects.create(user=self.user)
        forum = Forum.objects.create(
            category=Category.objects.create(name="Cat"), name="Forum"
        )
        self.topic = Topic.objects.create(forum=forum, name="Topic", user=self.user)
        self.topic.subscribers.add(self.user)
        NoticeType.objects.create(label="test_notice", display="d", description="d")
        observe(self.topic, self.user, "test_notice")
        self.client.force_login(self.user)

    def _observed_count(self):
        from notification.models import ObservedItem

        return ObservedItem.objects.filter(user=self.user).count()

    def test_do_delete_get_is_rejected(self):
        response = self.client.get(reverse("do_delete"))
        self.assertEqual(response.status_code, 405)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.email, "alice@example.com")

    def test_do_delete_post_deactivates_user(self):
        response = self.client.post(reverse("do_delete"))
        self.assertRedirects(
            response, reverse("mainpage"), fetch_redirect_response=False
        )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unsubscribe_topics_get_is_rejected(self):
        response = self.client.get(reverse("unsubscribe_topics"))
        self.assertEqual(response.status_code, 405)
        self.assertIn(self.user, self.topic.subscribers.all())

    def test_unsubscribe_topics_post_unsubscribes(self):
        response = self.client.post(reverse("unsubscribe_topics"))
        self.assertRedirects(response, reverse("subscriptions"))
        self.assertNotIn(self.user, self.topic.subscribers.all())

    def test_unsubscribe_other_get_is_rejected(self):
        response = self.client.get(reverse("unsubscribe_other"))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self._observed_count(), 1)

    def test_unsubscribe_other_post_unsubscribes(self):
        response = self.client.post(reverse("unsubscribe_other"))
        self.assertRedirects(response, reverse("subscriptions"))
        self.assertEqual(self._observed_count(), 0)

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()
        for name in ("do_delete", "unsubscribe_topics", "unsubscribe_other"):
            response = self.client.post(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn(settings.LOGIN_URL, response["Location"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIn(self.user, self.topic.subscribers.all())


class TestAvatarUpload(TestCase):
    def setUp(self):
        self.profile = User.objects.create_user("avatar_user").wlprofile

    def _form_with_png(self, size):
        png = BytesIO()
        Image.new("1", size).save(png, format="PNG")
        upload = SimpleUploadedFile("avatar.png", png.getvalue(), "image/png")
        return EditProfileForm({}, {"avatar": upload}, instance=self.profile)

    def test_huge_image_is_rejected_before_decoding(self):
        form = self._form_with_png((5000, 4000))
        with mock.patch("wlprofile.fields.ExtendedImageField.resize_image") as resize:
            form.is_valid()

        self.assertIn("avatar", form.errors)
        resize.assert_not_called()

    def test_image_is_resized_to_avatar_size(self):
        form = self._form_with_png((300, 200))
        form.is_valid()

        self.assertNotIn("avatar", form.errors)
        avatar = Image.open(form.instance.avatar)
        self.assertEqual(avatar.size, (settings.AVATAR_WIDTH, settings.AVATAR_HEIGHT))
