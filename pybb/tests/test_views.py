from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from pybb.models import Category, Forum, Post, Topic


class _ForumTestBase(TestCase):
    """Sets up a forum with a topic, a moderator, and a regular user."""

    def setUp(self):
        self.mod_group = Group.objects.create(name="mods")

        self.moderator = User.objects.create_user(
            username="moderator", password="pass"
        )
        self.moderator.groups.add(self.mod_group)

        self.regular_user = User.objects.create_user(
            username="regular", password="pass"
        )

        self.category = Category.objects.create(name="General")
        self.forum = Forum.objects.create(
            category=self.category,
            name="Test Forum",
            moderator_group=self.mod_group,
        )
        self.topic = Topic.objects.create(
            forum=self.forum, name="Test Topic", user=self.moderator
        )
        Post.objects.create(
            topic=self.topic, user=self.moderator, body="First post", markup="markdown"
        )


class TestStickTopic(_ForumTestBase):
    def test_get_rejected(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_stick_topic", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.topic.refresh_from_db()
        self.assertFalse(self.topic.sticky)

    def test_post_by_moderator(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_stick_topic", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertTrue(self.topic.sticky)

    def test_post_by_regular_user_no_effect(self):
        self.client.login(username="regular", password="pass")
        url = reverse("pybb_stick_topic", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertFalse(self.topic.sticky)


class TestUnstickTopic(_ForumTestBase):
    def setUp(self):
        super().setUp()
        self.topic.sticky = True
        self.topic.save()

    def test_get_rejected(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_unstick_topic", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.topic.refresh_from_db()
        self.assertTrue(self.topic.sticky)

    def test_post_by_moderator(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_unstick_topic", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertFalse(self.topic.sticky)


class TestCloseTopic(_ForumTestBase):
    def test_get_rejected(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_close_topic", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.topic.refresh_from_db()
        self.assertFalse(self.topic.closed)

    def test_post_by_moderator(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_close_topic", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertTrue(self.topic.closed)


class TestOpenTopic(_ForumTestBase):
    def setUp(self):
        super().setUp()
        self.topic.closed = True
        self.topic.save()

    def test_get_rejected(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_open_topic", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.topic.refresh_from_db()
        self.assertTrue(self.topic.closed)

    def test_post_by_moderator(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_open_topic", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertFalse(self.topic.closed)


class TestToggleHiddenTopic(_ForumTestBase):
    def test_get_rejected(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_toggle_hid_topic", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_post_toggles_hidden(self):
        self.client.login(username="moderator", password="pass")
        url = reverse("pybb_toggle_hid_topic", args=[self.topic.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        first_post = self.topic.posts.first()
        self.assertTrue(first_post.hidden)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        first_post.refresh_from_db()
        self.assertFalse(first_post.hidden)

    def test_post_by_regular_user_no_effect(self):
        first_post = self.topic.posts.first()
        first_post.hidden = True
        first_post.save()
        self.client.login(username="regular", password="pass")
        url = reverse("pybb_toggle_hid_topic", args=[self.topic.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        first_post.refresh_from_db()
        self.assertTrue(first_post.hidden)

    def test_anonymous_rejected(self):
        url = reverse("pybb_toggle_hid_topic", args=[self.topic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.assertIn("login", response.url)
