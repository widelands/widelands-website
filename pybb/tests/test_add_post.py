from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from pybb.models import Category, Forum, Post, Topic


class TestAddPostAccess(TestCase):
    """Adding posts and quoting must respect what show_topic lets a user see."""

    def setUp(self):
        self.mod_group = Group.objects.create(name="mods")
        self.moderator = User.objects.create_user(username="moderator", password="pass")
        self.moderator.groups.add(self.mod_group)
        self.regular_user = User.objects.create_user(
            username="regular", password="pass"
        )
        self.internal_user = User.objects.create_user(
            username="internal", password="pass"
        )
        self.internal_user.user_permissions.add(
            Permission.objects.get(codename="can_access_internal")
        )

        self.forum, self.topic, self.post = self._create_topic(internal=False)
        self.hidden_post = Post.objects.create(
            topic=self.topic,
            user=self.moderator,
            body="Hidden spam body",
            markup="markdown",
            hidden=True,
        )
        self.internal_forum, self.internal_topic, self.internal_post = (
            self._create_topic(internal=True)
        )

    def _create_topic(self, internal):
        category = Category.objects.create(
            name="Internal" if internal else "General", internal=internal
        )
        forum = Forum.objects.create(
            category=category, name="Forum", moderator_group=self.mod_group
        )
        topic = Topic.objects.create(forum=forum, name="Topic", user=self.moderator)
        post = Post.objects.create(
            topic=topic,
            user=self.moderator,
            body="Secret internal body" if internal else "Public body",
            markup="markdown",
        )
        return forum, topic, post

    def _quote(self, user, topic, post):
        self.client.force_login(user)
        url = reverse("pybb_add_post", args=[topic.id])
        return self.client.get(url, {"quote_id": post.id})

    def test_quote_of_visible_post(self):
        response = self._quote(self.regular_user, self.topic, self.post)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public body")

    def test_regular_user_cannot_quote_internal_post(self):
        response = self._quote(self.regular_user, self.topic, self.internal_post)
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Secret internal body", status_code=404)

    def test_regular_user_cannot_quote_hidden_post(self):
        response = self._quote(self.regular_user, self.topic, self.hidden_post)
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Hidden spam body", status_code=404)

    def test_moderator_can_quote_hidden_post(self):
        response = self._quote(self.moderator, self.topic, self.hidden_post)
        self.assertContains(response, "Hidden spam body")

    def test_cannot_quote_post_of_another_topic(self):
        # Even a user allowed to see the internal post may only quote posts of
        # the topic being replied to.
        response = self._quote(self.internal_user, self.topic, self.internal_post)
        self.assertEqual(response.status_code, 404)

    def test_internal_user_can_quote_internal_post(self):
        response = self._quote(
            self.internal_user, self.internal_topic, self.internal_post
        )
        self.assertContains(response, "Secret internal body")

    def test_regular_user_cannot_reply_to_internal_topic(self):
        self.client.force_login(self.regular_user)
        url = reverse("pybb_add_post", args=[self.internal_topic.id])
        self.assertEqual(self.client.get(url).status_code, 404)
        response = self.client.post(url, {"body": "Intruder", "markup": "markdown"})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Post.objects.filter(body="Intruder").exists())
        self.assertNotIn(self.regular_user, self.internal_topic.subscribers.all())

    def test_regular_user_cannot_add_topic_to_internal_forum(self):
        self.client.force_login(self.regular_user)
        url = reverse("pybb_add_topic", args=[self.internal_forum.id])
        response = self.client.post(
            url, {"name": "Intruder topic", "body": "Intruder", "markup": "markdown"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Topic.objects.filter(name="Intruder topic").exists())

    def test_internal_user_can_reply_to_internal_topic(self):
        self.client.force_login(self.internal_user)
        url = reverse("pybb_add_post", args=[self.internal_topic.id])
        response = self.client.post(url, {"body": "Insider", "markup": "markdown"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Post.objects.filter(topic=self.internal_topic, body="Insider").exists()
        )

    def test_internal_user_can_add_topic_to_internal_forum(self):
        self.client.force_login(self.internal_user)
        url = reverse("pybb_add_topic", args=[self.internal_forum.id])
        response = self.client.post(
            url, {"name": "Insider topic", "body": "Insider", "markup": "markdown"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Topic.objects.filter(
                forum=self.internal_forum, name="Insider topic"
            ).exists()
        )

    def test_regular_user_cannot_subscribe_to_internal_topic(self):
        self.client.force_login(self.regular_user)
        url = reverse("pybb_add_subscription", args=[self.internal_topic.id])
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertNotIn(self.regular_user, self.internal_topic.subscribers.all())

    def test_internal_user_can_subscribe_to_internal_topic(self):
        self.client.force_login(self.internal_user)
        url = reverse("pybb_add_subscription", args=[self.internal_topic.id])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertIn(self.internal_user, self.internal_topic.subscribers.all())
