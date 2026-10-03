from unittest import mock

from django.contrib.auth.models import User
from django.core import mail, signing
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_registration.backends.activation import REGISTRATION_SALT

STRONG_PASSWORD = "correct horse battery staple"


@mock.patch("django_recaptcha.fields.ReCaptchaField.validate")
class TestRegistration(TestCase):
    def _register(self, password):
        return self.client.post(
            reverse("django_registration_register"),
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password1": password,
                "password2": password,
                "g-recaptcha-response": "ok",
            },
        )

    def test_weak_password_is_rejected(self, _validate):
        response = self._register("12345678")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["password2"])
        self.assertFalse(User.objects.filter(username="newbie").exists())

    def test_activation_link_uses_https(self, _validate):
        response = self._register(STRONG_PASSWORD)

        self.assertRedirects(response, reverse("django_registration_complete"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("https://", mail.outbox[0].body)
        self.assertNotIn("http://", mail.outbox[0].body)


class TestPasswordChange(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", password=STRONG_PASSWORD)
        self.client.force_login(self.user)

    def _change(self, new_password):
        return self.client.post(
            reverse("password_change"),
            {
                "old_password": STRONG_PASSWORD,
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )

    def test_common_password_is_rejected(self):
        response = self._change("password")

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(STRONG_PASSWORD))

    def test_strong_password_is_accepted(self):
        response = self._change("another long passphrase")

        self.assertRedirects(response, reverse("password_change_done"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("another long passphrase"))


class TestActivation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "user", "user@example.com", STRONG_PASSWORD, is_active=False
        )

    def _activate(self):
        key = signing.dumps(obj="user", salt=REGISTRATION_SALT)
        response = self.client.post(
            reverse("django_registration_activate"), {"activation_key": key}
        )
        self.user.refresh_from_db()
        return response

    def test_new_account_is_activated(self):
        response = self._activate()

        self.assertRedirects(
            response, reverse("django_registration_activation_complete")
        )
        self.assertTrue(self.user.is_active)

    def test_banned_account_is_not_reactivated(self):
        # Banned accounts have logged in before they were deactivated.
        self.user.last_login = timezone.now()
        self.user.save()

        response = self._activate()

        self.assertEqual(
            response.context["activation_error"]["code"], "account_disabled"
        )
        self.assertFalse(self.user.is_active)

    def test_deleted_account_is_not_reactivated(self):
        self.user.wlprofile.deleted = True
        self.user.wlprofile.save()

        response = self._activate()

        self.assertEqual(
            response.context["activation_error"]["code"], "account_disabled"
        )
        self.assertFalse(self.user.is_active)


class TestEmailChange(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "old@example.com", STRONG_PASSWORD)
        self.client.force_login(self.user)

    def _edit(self, **data):
        data.setdefault("email", "old@example.com")
        data.setdefault("time_zone", "0.0")
        data.setdefault("time_display", "%ND(Y-m-d,) H:i e")
        response = self.client.post(reverse("profile_edit"), data)
        self.user.refresh_from_db()
        return response

    def test_change_without_password_is_rejected(self):
        response = self._edit(email="attacker@example.com")

        self.assertEqual(response.status_code, 200)
        self.assertIn("current_password", response.context["profile_form"].errors)
        self.assertEqual(self.user.email, "old@example.com")
        self.assertEqual(mail.outbox, [])

    def test_change_with_wrong_password_is_rejected(self):
        self._edit(email="attacker@example.com", current_password="wrong")

        self.assertEqual(self.user.email, "old@example.com")

    def test_change_with_password_notifies_old_address(self):
        response = self._edit(email="new@example.com", current_password=STRONG_PASSWORD)

        self.assertRedirects(response, reverse("profile_view"))
        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["old@example.com"])
        self.assertIn("new@example.com", mail.outbox[0].body)

    def test_other_fields_need_no_password(self):
        response = self._edit(location="Somewhere")

        self.assertRedirects(response, reverse("profile_view"))
        self.assertEqual(self.user.wlprofile.location, "Somewhere")
        self.assertEqual(mail.outbox, [])
