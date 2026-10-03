import base64
import hashlib
from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import GGZAuth


def b64sha1(pw):
    return base64.standard_b64encode(hashlib.sha1(pw.encode("utf-8")).digest()).decode(
        "ascii"
    )


class GGZAuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "a@example.com", "webpw")
        self.client.force_login(self.user)
        self.url = reverse("wlggz_changepw")

    def test_get_creates_no_row(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GGZAuth.objects.filter(user=self.user).exists())

    def test_post_creates_row_with_hash(self):
        self.client.post(self.url, {"password": "secret", "password2": "secret"})
        self.assertEqual(
            GGZAuth.objects.get(user=self.user).password, b64sha1("secret")
        )

    def test_post_updates_existing_row(self):
        GGZAuth.objects.create(user=self.user, password=b64sha1("old"), permissions=3)
        self.client.post(self.url, {"password": "new", "password2": "new"})
        row = GGZAuth.objects.get(user=self.user)
        self.assertEqual(row.password, b64sha1("new"))
        self.assertEqual(row.permissions, 3)

    def test_mismatched_post_creates_no_row(self):
        self.client.post(self.url, {"password": "a", "password2": "b"})
        self.assertFalse(GGZAuth.objects.filter(user=self.user).exists())

    def test_resave_does_not_rehash(self):
        row = GGZAuth.objects.create(user=self.user, password=b64sha1("secret"))
        row.save()
        row.refresh_from_db()
        self.assertEqual(row.password, b64sha1("secret"))

    def test_admin_save_does_not_rehash(self):
        User.objects.create_superuser("root", "r@example.com", "rootpw")
        self.client.login(username="root", password="rootpw")
        row = GGZAuth.objects.create(user=self.user, password=b64sha1("secret"))
        url = reverse("admin:wlggz_ggzauth_change", args=[row.pk])
        self.client.post(url, {"user": self.user.pk, "permissions": 5})
        row.refresh_from_db()
        self.assertEqual(row.permissions, 5)
        self.assertEqual(row.password, b64sha1("secret"))

    def test_deactivating_user_deletes_row(self):
        other = User.objects.create_user("bob", "b@example.com", "pw")
        GGZAuth.objects.create(user=self.user, password=b64sha1("secret"))
        GGZAuth.objects.create(user=other, password=b64sha1("secret"))
        self.user.is_active = False
        self.user.save()
        self.assertFalse(GGZAuth.objects.filter(user=self.user).exists())
        self.assertTrue(GGZAuth.objects.filter(user=other).exists())

    def test_migration_deletes_only_unset_passwords(self):
        migration = import_module("wlggz.migrations.0003_delete_empty_passwords")
        users = [User.objects.create_user(f"u{i}") for i in range(4)]
        for user, pw in zip(users, ["", b64sha1(""), b64sha1("secret"), "x"]):
            GGZAuth.objects.create(user=user, password=pw)
        migration.delete_empty_passwords(apps, None)
        self.assertEqual(
            sorted(GGZAuth.objects.values_list("password", flat=True)),
            sorted([b64sha1("secret"), "x"]),
        )
