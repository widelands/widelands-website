from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_messages.models import Message

from news.models import Post as NewsPost
from pybb.models import Category, Forum, Topic, Post
from threadedcomments.models import ThreadedComment
from .admin import delete_objects, unhide_post
from .models import SuspiciousInput
from .models import SuspiciousKeyword


class SuspiciousModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.spam_keywords = SuspiciousKeyword.objects.create(keyword="spamword")
        cls.test_user = User.objects.create_user(
            "donald", "donald@duck.de", "donaldpwd"
        )
        cls.forum_category = Category.objects.create(
            name="forum_cat", position=1, internal=False
        )
        cls.forum_forum = Forum.objects.create(category=cls.forum_category)
        cls.forum_topic = Topic.objects.create(
            forum=cls.forum_forum, user=cls.test_user, name="test spam"
        )
        cls.forum_post = Post.objects.create(
            topic=cls.forum_topic, user=cls.test_user, body="testing"
        )

    def test_spam_topic(self):
        spam_topic_text_with_spam = "This topic is spamword"
        susp_input = SuspiciousInput(
            content_object=self.forum_topic,
            user=self.test_user,
            text=spam_topic_text_with_spam,
        )
        result = susp_input.is_suspicious()
        self.assertEqual(result, True, "Should be spam")

    def test_no_spam_topic(self):
        spam_topic_text_without_spam = "This topic is fine"
        susp_input = SuspiciousInput(
            content_object=self.forum_topic,
            user=self.test_user,
            text=spam_topic_text_without_spam,
        )
        result = susp_input.is_suspicious()
        self.assertEqual(result, False)

    def test_no_spam_post(self):
        spam_text_without_spam = "We like widelands"
        susp_input = SuspiciousInput(
            content_object=self.forum_post,
            user=self.test_user,
            text=spam_text_without_spam,
        )
        result = susp_input.is_suspicious()
        self.assertEqual(result, False)

    def test_spam_post_long_end(self):
        text_with_spam_end = "x" * 220 + "spamword"
        susp_input = SuspiciousInput(
            content_object=self.forum_post, user=self.test_user, text=text_with_spam_end
        )
        result = susp_input.is_suspicious()
        self.assertEqual(result, True)

    def test_suspicious_text_length(self):
        text_with_spam_at_middle = "x" * 110 + "spamword" + "x" * 110
        susp_input = SuspiciousInput(
            content_object=self.forum_post,
            user=self.test_user,
            text=text_with_spam_at_middle,
        )
        susp_input.is_suspicious()
        self.assertEqual(
            len(susp_input.text),
            SuspiciousInput._meta.get_field("text").max_length,
            msg="Test with spam at MIDDLE failed",
        )

        text_with_spam_at_start = "spamword" + "x" * 220
        susp_input = SuspiciousInput(
            content_object=self.forum_post,
            user=self.test_user,
            text=text_with_spam_at_start,
        )
        susp_input.is_suspicious()
        self.assertEqual(
            len(susp_input.text),
            SuspiciousInput._meta.get_field("text").max_length,
            "Test with spam at START failed",
        )

        text_with_spam_at_end = "x" * 220 + "spamword"
        susp_input = SuspiciousInput(
            content_object=self.forum_post,
            user=self.test_user,
            text=text_with_spam_at_end,
        )
        susp_input.is_suspicious()
        self.assertEqual(
            len(susp_input.text),
            SuspiciousInput._meta.get_field("text").max_length,
            msg="Test with spam at END failed",
        )


@override_settings(MAX_HIDDEN_POSTS=2)
class SpamLockoutTests(TestCase):
    def setUp(self):
        SuspiciousKeyword.objects.create(keyword="spamword")
        self.user = User.objects.create_user("spammer", password="pass")
        category = Category.objects.create(name="General")
        forum = Forum.objects.create(category=category, name="Forum")
        self.topic = Topic.objects.create(forum=forum, name="Topic", user=self.user)
        self.post = Post.objects.create(topic=self.topic, user=self.user, body="Hi")

    def _flag(self):
        return SuspiciousInput.check_input(
            content_object=self.post, user=self.user, text="spamword"
        )

    def test_check_input_deactivates_user_at_limit(self):
        self.assertTrue(self._flag())
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self._flag())
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_lockout_does_not_need_the_redirect(self):
        self.client.force_login(self.user)
        url = reverse("pybb_add_post", args=[self.topic.id])
        for _ in range(2):
            response = self.client.post(
                url, {"body": "buy spamword", "markup": "markdown"}
            )
            self.assertRedirects(response, "/moderated/", fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_moderated_page_warns_before_limit(self):
        self.client.force_login(self.user)
        self._flag()
        response = self.client.get("/moderated/")
        self.assertContains(response, "The next time you will get logged out")
        self.assertIn(SESSION_KEY, self.client.session)

    def test_moderated_page_logs_out_locked_user(self):
        self.client.force_login(self.user)
        self._flag()
        self._flag()
        response = self.client.get("/moderated/")
        self.assertContains(response, "You can't login anymore")
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_moderated_page_without_flagged_input_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get("/moderated/")
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.client.logout()
        response = self.client.get("/moderated/")
        self.assertRedirects(response, "/", fetch_redirect_response=False)


class ModerationActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("spammer")
        self.post = NewsPost.objects.create(
            title="News",
            slug="news",
            author=self.user,
            body="Body",
            publish=timezone.now(),
        )

    def test_unhide_comment(self):
        comment = ThreadedComment.objects.create(
            content_object=self.post, user=self.user, comment="x", is_public=False
        )
        SuspiciousInput.objects.create(content_object=comment, user=self.user, text="x")
        unhide_post(None, None, SuspiciousInput.objects.all())
        comment.refresh_from_db()
        self.assertTrue(comment.is_public)
        self.assertFalse(SuspiciousInput.objects.exists())

    def test_actions_on_refused_message(self):
        message_type = ContentType.objects.get_for_model(Message)
        for action in (unhide_post, delete_objects):
            SuspiciousInput.objects.create(
                content_type=message_type, user=self.user, text="x"
            )
            action(None, None, SuspiciousInput.objects.all())
            self.assertFalse(SuspiciousInput.objects.exists())
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
