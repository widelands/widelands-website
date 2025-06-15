from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from pybb.models import Category, Forum, Topic, Post
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
