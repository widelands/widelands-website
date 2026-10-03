from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from django_messages.models import Message


class MessageViewsTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.recipient = User.objects.create_user(username="recipient", password="pass")
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject="Subject",
            body="Body",
        )
        self.client.login(username="recipient", password="pass")
        self.delete_url = reverse("messages_delete", args=[self.message.id])
        self.undelete_url = reverse("messages_undelete", args=[self.message.id])

    def test_delete_rejects_get(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 405)
        self.message.refresh_from_db()
        self.assertIsNone(self.message.recipient_deleted_at)

    def test_undelete_rejects_get(self):
        Message.objects.filter(pk=self.message.pk).update(
            recipient_deleted_at=timezone.now()
        )
        response = self.client.get(self.undelete_url)
        self.assertEqual(response.status_code, 405)
        self.message.refresh_from_db()
        self.assertIsNotNone(self.message.recipient_deleted_at)

    def test_delete_post_redirects_to_local_next(self):
        response = self.client.post(self.delete_url, {"next": "/messages/outbox/"})
        self.assertRedirects(
            response, "/messages/outbox/", fetch_redirect_response=False
        )
        self.message.refresh_from_db()
        self.assertIsNotNone(self.message.recipient_deleted_at)
        self.assertIsNone(self.message.sender_deleted_at)

    def test_delete_post_ignores_offsite_next(self):
        evil = "https://evil.example/"
        response = self.client.post(f"{self.delete_url}?next={evil}", {"next": evil})
        self.assertRedirects(
            response, reverse("messages_inbox"), fetch_redirect_response=False
        )
        self.message.refresh_from_db()
        self.assertIsNotNone(self.message.recipient_deleted_at)

    def test_undelete_post_ignores_offsite_next(self):
        Message.objects.filter(pk=self.message.pk).update(
            recipient_deleted_at=timezone.now()
        )
        evil = "//evil.example/"
        response = self.client.post(f"{self.undelete_url}?next={evil}", {"next": evil})
        self.assertRedirects(
            response, reverse("messages_inbox"), fetch_redirect_response=False
        )
        self.message.refresh_from_db()
        self.assertIsNone(self.message.recipient_deleted_at)

    def test_compose_ignores_offsite_next(self):
        response = self.client.post(
            reverse("messages_compose") + "?next=https://evil.example/",
            {"recipient": "sender", "subject": "Hi", "body": "Hello"},
        )
        self.assertRedirects(
            response, reverse("messages_inbox"), fetch_redirect_response=False
        )
        self.assertTrue(Message.objects.filter(subject="Hi").exists())
