from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from notification.models import NoticeSetting, NoticeType, send_now
from pybb.models import Category, Forum, Post, Topic

EVIL = '<a href="https://evil.example/">click</a>'
ESCAPED_EVIL = "&lt;a href=&quot;https://evil.example/&quot;&gt;click&lt;/a&gt;"


class TestHtmlMailEscaping(TestCase):
    """User supplied plain text must not become markup in HTML mails."""

    def setUp(self):
        self.reader = User.objects.create(username="reader", email="reader@example.com")
        self.author = User.objects.create(username="author")

    def _html_mail(self, label, context):
        NoticeSetting.objects.update_or_create(
            user=self.reader,
            notice_type=NoticeType.objects.get(label=label),
            defaults={"send": True},
        )
        send_now([self.reader], label, context)
        (message,) = mail.outbox
        html, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        return html

    def test_forum_mails(self):
        category = Category.objects.create(name="General")
        forum = Forum.objects.create(category=category, name="Forum")
        topic = Topic.objects.create(forum=forum, name=EVIL, user=self.author)
        post = Post.objects.create(
            topic=topic, user=self.author, body="**bold**", markup="markdown"
        )
        for label in ("forum_new_topic", "forum_new_post", "forum_mention"):
            with self.subTest(label=label):
                mail.outbox.clear()
                html = self._html_mail(
                    label, {"topic": topic, "post": post, "user": self.author}
                )
                self.assertNotIn(EVIL, html)
                self.assertIn(ESCAPED_EVIL, html)
                # The rendered post itself is (bleached) HTML
                self.assertIn("<strong>bold</strong>", html)

    def test_new_map_mail(self):
        html = self._html_mail(
            "maps_new_map",
            {
                "mapname": EVIL,
                "uploader_comment": EVIL,
                "url": "/maps/evil/",
                "user": self.author,
            },
        )
        self.assertNotIn(EVIL, html)
        self.assertEqual(html.count(ESCAPED_EVIL), 3)

    def test_wiki_article_changed_mail(self):
        html = self._html_mail(
            "wiki_observed_article_changed",
            {"editor": self.author, "rev": 2, "rev_comment": EVIL, "article": "Page"},
        )
        self.assertNotIn(EVIL, html)
        self.assertIn(ESCAPED_EVIL, html)
