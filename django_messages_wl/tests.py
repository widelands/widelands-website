from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse
from django_messages.models import Message

from check_input.models import SuspiciousInput, SuspiciousKeyword


@override_settings(MAX_HIDDEN_POSTS=2)
class ComposeSpamCheckTestCase(TestCase):
    def setUp(self):
        SuspiciousKeyword.objects.create(keyword="spamword")
        self.sender = User.objects.create_user(username="sender", password="pass")
        self.recipient = User.objects.create_user(username="recipient")
        self.client.login(username="sender", password="pass")

    def _send(self, body, url=None):
        return self.client.post(
            url or reverse("messages_compose"),
            {"recipient": "recipient", "subject": "Hello", "body": body},
        )

    def test_spam_message_is_refused_and_recorded(self):
        response = self._send("buy spamword now")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This message looks like spam and was not sent.")
        self.assertFalse(Message.objects.exists())
        flagged = SuspiciousInput.objects.get()
        self.assertEqual(flagged.user, self.sender)
        self.assertEqual(
            flagged.content_type, ContentType.objects.get_for_model(Message)
        )
        self.assertIsNone(flagged.object_id)

    def test_spam_in_subject_is_refused(self):
        response = self.client.post(
            reverse("messages_compose"),
            {"recipient": "recipient", "subject": "spamword", "body": "Hi"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Message.objects.exists())

    def test_clean_message_is_delivered(self):
        response = self._send("nice to meet you")
        self.assertRedirects(
            response, reverse("messages_inbox"), fetch_redirect_response=False
        )
        message = Message.objects.get()
        self.assertEqual(message.recipient, self.recipient)
        self.assertEqual(message.body, "nice to meet you")
        self.assertFalse(SuspiciousInput.objects.exists())

    def test_spam_reply_is_refused(self):
        parent = Message.objects.create(
            sender=self.recipient, recipient=self.sender, subject="Hi", body="Hi"
        )
        response = self._send(
            "spamword", url=reverse("messages_reply", args=[parent.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(Message.objects.all()), [parent])
        self.assertTrue(SuspiciousInput.objects.filter(user=self.sender).exists())

    def test_invalid_message_is_not_checked(self):
        response = self.client.post(
            reverse("messages_compose"),
            {"recipient": "nobody", "subject": "Hello", "body": "spamword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SuspiciousInput.objects.exists())

    def test_spam_messages_lock_out_user(self):
        response = self._send("spamword one")
        self.assertContains(response, "The next time your account will be deactivated")
        self.sender.refresh_from_db()
        self.assertTrue(self.sender.is_active)
        response = self._send("spamword two")
        self.assertContains(response, "Your account has been deactivated.")
        self.sender.refresh_from_db()
        self.assertFalse(self.sender.is_active)
        self.assertFalse(Message.objects.exists())
