from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(ADMINS=[("Admin", "admin@example.com")])
class LoginTimezoneTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("victim", password="secret")
        self.user.wlprofile.time_zone = 1.0
        self.user.wlprofile.save()

    def _login(self, password, browser_timezone, set_timezone=True):
        data = {
            "username": "victim",
            "password": password,
            "browser_timezone": browser_timezone,
        }
        if set_timezone:
            data["set_timezone"] = "on"
        return self.client.post(reverse("login"), data)

    def _time_zone(self):
        self.user.wlprofile.refresh_from_db()
        return self.user.wlprofile.time_zone

    def test_failed_login_does_not_change_time_zone(self):
        for password in ("", "wrong"):
            with self.subTest(password=password):
                self._login(password, "5")
                self.assertEqual(self._time_zone(), 1.0)
                self.assertNotIn("_auth_user_id", self.client.session)

    def test_failed_login_with_unknown_time_zone_sends_no_mail(self):
        for password in ("", "wrong"):
            with self.subTest(password=password):
                self._login(password, "1.234")
                self.assertEqual(mail.outbox, [])

    def test_successful_login_updates_own_time_zone(self):
        self._login("secret", "5")
        self.assertEqual(self._time_zone(), 5.0)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_successful_login_without_checkbox_keeps_time_zone(self):
        self._login("secret", "5", set_timezone=False)
        self.assertEqual(self._time_zone(), 1.0)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)
