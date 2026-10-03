from unittest import mock

from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from pybb import settings as pybb_settings
from pybb.models import Post, Topic
from pybb.tests.test_views import _ForumTestBase


class TestLatestPosts(_ForumTestBase):
    def setUp(self):
        super().setUp()
        # Eight topics fill the "latest posts" sidebar box.
        self.topics = []
        for i in range(8):
            user = User.objects.create_user(username=f"poster{i}", password="pass")
            topic = Topic.objects.create(forum=self.forum, name=f"Topic {i}", user=user)
            Post.objects.create(
                topic=topic, user=user, body=f"Post {i}", markup="markdown"
            )
            self.topics.append(topic)

    def _num_queries(self, sort_by):
        url = reverse("all_latest_posts")
        params = {"days": 30, "sort_by": sort_by}
        self.client.get(url, params)  # creates missing user profiles
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        return len(queries)

    def test_days_are_bounded(self):
        response = self.client.get(reverse("all_latest_posts"), {"days": 1000})
        self.assertIn("days", response.context["form"].errors)

    def test_number_of_posts_is_capped(self):
        with mock.patch.object(pybb_settings, "LAST_POSTS_LIMIT", 2):
            response = self.client.get(reverse("all_latest_posts"))
        self.assertEqual(response.context["posts_count"], 2)
        self.assertContains(response, "Showing only the 2 most recent posts")
        self.assertNotContains(response, "First post")

    def test_queries_do_not_grow_with_posts(self):
        few = {s: self._num_queries(s) for s in ("topic", "forum")}
        for topic in self.topics:
            Post.objects.create(
                topic=topic, user=topic.user, body="More", markup="markdown"
            )
        many = {s: self._num_queries(s) for s in ("topic", "forum")}
        self.assertEqual(few, many)


class TestTopicAttachments(_ForumTestBase):
    def _attachment_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse("pybb_topic", args=[self.topic.id]))
        self.assertEqual(response.status_code, 200)
        return len([q for q in queries if 'FROM "pybb_attachment"' in q["sql"]])

    def _add_replies(self, count):
        for i in range(count):
            Post.objects.create(
                topic=self.topic,
                user=self.regular_user,
                body=f"Reply {i}",
                markup="markdown",
            )

    def test_attachment_queries_do_not_grow_with_posts(self):
        self._add_replies(1)
        few = self._attachment_queries()
        self._add_replies(5)
        self.assertEqual(self._attachment_queries(), few)


class TestUsernameAutocomplete(_ForumTestBase):
    URLS = (
        "/forum/get_tribute_usernames/",
        "/messages/django_messages_wl/get_usernames/",
    )

    def setUp(self):
        super().setUp()
        for i in range(25):
            User.objects.create_user(username=f"player{i:02}", password="pass")
        self.client.force_login(self.regular_user)

    def _get(self, url, term):
        response = self.client.get(
            url, {"term": term}, headers={"x-requested-with": "XMLHttpRequest"}
        )
        return response.json()

    def test_results_are_limited(self):
        for url in self.URLS:
            self.assertEqual(len(self._get(url, "player")), 20)

    def test_short_term_gives_no_results(self):
        for url in self.URLS:
            self.assertEqual(self._get(url, ""), [])
            self.assertEqual(self._get(url, "p"), [])
