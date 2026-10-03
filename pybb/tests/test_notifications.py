from django.contrib.auth.models import Permission, User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from notification.models import NoticeSetting, NoticeType
from pybb import settings as pybb_settings
from pybb.models import Category, Forum, Post, Topic


class _NotificationTestBase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", password="pass", email="author@example.com"
        )
        self.victim = User.objects.create(username="victim", email="victim@example.com")
        self.insider = User.objects.create(
            username="insider", email="insider@example.com"
        )
        internal_perm = Permission.objects.get(codename="can_access_internal")
        self.author.user_permissions.add(internal_perm)
        self.insider.user_permissions.add(internal_perm)

        self.topic = self._create_topic(internal=False)
        self.internal_topic = self._create_topic(internal=True)

    def _create_topic(self, internal):
        category = Category.objects.create(
            name="Internal" if internal else "General", internal=internal
        )
        forum = Forum.objects.create(category=category, name="Forum")
        topic = Topic.objects.create(forum=forum, name="Topic", user=self.author)
        Post.objects.create(
            topic=topic, user=self.author, body="First post", markup="markdown"
        )
        return topic

    def _reply(self, topic, body):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("pybb_add_post", args=[topic.id]),
            {"body": body, "markup": "markdown"},
        )
        self.assertEqual(response.status_code, 302)
        return topic.posts.order_by("id").last()

    def _edit(self, post, body):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("pybb_edit_post", args=[post.id]),
            {"body": body, "markup": "markdown"},
        )
        self.assertEqual(response.status_code, 302)

    def _mails_to(self, user):
        return [m for m in mail.outbox if m.to == [user.email]]

    def _observe_new_topics(self, user):
        NoticeSetting.objects.update_or_create(
            user=user,
            notice_type=NoticeType.objects.get(label="forum_new_topic"),
            defaults={"send": True},
        )


class TestMentions(_NotificationTestBase):
    def test_repeated_mention_sends_one_mail(self):
        self._reply(self.topic, "@victim " * 20)
        self.assertEqual(len(self._mails_to(self.victim)), 1)

    def test_mentions_are_capped(self):
        users = [
            User.objects.create(username=f"user{i}", email=f"user{i}@example.com")
            for i in range(pybb_settings.MAX_MENTIONS + 5)
        ]
        self._reply(self.topic, " ".join(f"@{user.username}" for user in users))
        self.assertEqual(len(mail.outbox), pybb_settings.MAX_MENTIONS)
        for user in users[: pybb_settings.MAX_MENTIONS]:
            self.assertEqual(len(self._mails_to(user)), 1)

    def test_author_is_not_informed_about_own_mention(self):
        self._reply(self.topic, "@author @victim")
        self.assertEqual(self._mails_to(self.author), [])
        self.assertEqual(len(self._mails_to(self.victim)), 1)

    def test_edit_informs_only_newly_mentioned_users(self):
        post = self._reply(self.topic, "Hello @victim")
        mail.outbox.clear()
        self._edit(post, "Hello @victim @victim @insider @insider")
        self.assertEqual(self._mails_to(self.victim), [])
        self.assertEqual(len(self._mails_to(self.insider)), 1)

    def test_edit_of_hidden_post_informs_nobody(self):
        post = Post.objects.create(
            topic=self.topic,
            user=self.author,
            body="Held back",
            markup="markdown",
            hidden=True,
        )
        self._edit(post, "Held back @victim")
        self.assertEqual(mail.outbox, [])

    def test_internal_post_mentions_only_users_with_access(self):
        self._reply(self.internal_topic, "@victim @insider")
        self.assertEqual(self._mails_to(self.victim), [])
        self.assertEqual(len(self._mails_to(self.insider)), 1)

    def test_internal_post_edit_mentions_only_users_with_access(self):
        post = self._reply(self.internal_topic, "Hello")
        self._edit(post, "Hello @victim @insider")
        self.assertEqual(self._mails_to(self.victim), [])
        self.assertEqual(len(self._mails_to(self.insider)), 1)


class TestUnhidePost(_NotificationTestBase):
    def _hidden_topic(self, topic):
        topic = Topic.objects.create(forum=topic.forum, name="Held", user=self.author)
        return Post.objects.create(
            topic=topic,
            user=self.author,
            body="Held back topic",
            markup="markdown",
            hidden=True,
        )

    def test_unhidden_internal_topic_goes_only_to_users_with_access(self):
        self._observe_new_topics(self.victim)
        self._observe_new_topics(self.insider)
        self._hidden_topic(self.internal_topic).unhide_post()
        self.assertEqual(self._mails_to(self.victim), [])
        self.assertEqual(len(self._mails_to(self.insider)), 1)

    def test_unhidden_topic_goes_to_new_topic_observers(self):
        self._observe_new_topics(self.victim)
        self._hidden_topic(self.topic).unhide_post()
        self.assertEqual(len(self._mails_to(self.victim)), 1)
        self.assertEqual(self._mails_to(self.insider), [])

    def test_unhidden_internal_post_goes_only_to_subscribers_with_access(self):
        self.internal_topic.subscribers.add(self.victim, self.insider)
        post = Post.objects.create(
            topic=self.internal_topic,
            user=self.author,
            body="Held back reply",
            markup="markdown",
            hidden=True,
        )
        post.unhide_post()
        self.assertEqual(self._mails_to(self.victim), [])
        self.assertEqual(len(self._mails_to(self.insider)), 1)
