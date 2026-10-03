from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from pybb.models import Category, Forum, Post, Reaction, Topic
from pybb.search_indexes import PostIndex
from pybb.sitemap import ForumSitemap
from pybb.tests.test_views import _ForumTestBase


class _HiddenTopicTestBase(_ForumTestBase):
    """Adds a topic whose first post is hidden (spam), written by `spammer`,
    and a public reply to it."""

    def setUp(self):
        super().setUp()
        self.spammer = User.objects.create_user(username="spammer", password="pass")
        self.hidden_topic = Topic.objects.create(
            forum=self.forum, name="Spam title", user=self.spammer
        )
        start = datetime.now() - timedelta(hours=1)
        self.hidden_head = Post.objects.create(
            topic=self.hidden_topic,
            user=self.spammer,
            body="Spam head",
            markup="markdown",
            hidden=True,
            created=start,
        )
        self.hidden_reply = Post.objects.create(
            topic=self.hidden_topic,
            user=self.regular_user,
            body="Reply in spam topic",
            markup="markdown",
            created=start + timedelta(minutes=1),
        )


class TestHiddenTopicQuerySet(_HiddenTopicTestBase):
    def test_hidden_is_decided_by_first_post(self):
        Post.objects.create(
            topic=self.topic,
            user=self.regular_user,
            body="Hidden reply",
            markup="markdown",
            hidden=True,
        )
        self.assertQuerySetEqual(Topic.objects.hidden(), [self.hidden_topic])

    def test_public_posts_exclude_hidden_topics_in_one_query(self):
        for i in range(3):
            topic = Topic.objects.create(
                forum=self.forum, name="Spam", user=self.spammer
            )
            Post.objects.create(
                topic=topic, user=self.spammer, body="x", markup="markdown", hidden=True
            )
        with self.assertNumQueries(1):
            bodies = [p.body for p in Post.objects.public()]
        self.assertEqual(bodies, ["First post"])

    def test_search_index_skips_posts_of_hidden_topics(self):
        indexed = PostIndex().index_queryset()
        self.assertNotIn(self.hidden_reply, indexed)
        self.assertIn(self.topic.posts.first(), indexed)


class TestHiddenTopicViews(_HiddenTopicTestBase):
    def test_topic_hidden_from_anonymous_and_regular_user(self):
        url = reverse("pybb_topic", args=[self.hidden_topic.id])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_author_only_sees_pending_notice(self):
        self.client.force_login(self.spammer)
        response = self.client.get(reverse("pybb_topic", args=[self.hidden_topic.id]))
        self.assertContains(response, "waiting for a review")
        self.assertNotContains(response, "Reply in spam topic")
        self.assertNotContains(
            response, reverse("pybb_add_post", args=[self.hidden_topic.id])
        )

    def test_moderator_sees_hidden_topic(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("pybb_topic", args=[self.hidden_topic.id]))
        self.assertContains(response, "Spam head")
        self.assertContains(response, "Reply in spam topic")

    def test_reply_to_hidden_topic_only_by_moderator(self):
        url = reverse("pybb_add_post", args=[self.hidden_topic.id])
        for user in (self.regular_user, self.spammer):
            self.client.force_login(user)
            response = self.client.post(url, {"body": "Reply", "markup": "markdown"})
            self.assertEqual(response.status_code, 404)
        self.assertEqual(self.hidden_topic.posts.count(), 2)

        self.client.force_login(self.moderator)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_show_post_of_hidden_topic_only_for_moderator(self):
        url = reverse("pybb_post", args=[self.hidden_reply.id])
        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.moderator)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"{reverse('pybb_topic', args=[self.hidden_topic.id])}?page=1"
            f"#post-{self.hidden_reply.id}",
        )


class TestShowPostReactions(_ForumTestBase):
    def setUp(self):
        super().setUp()
        self.post = self.topic.posts.first()
        self.url = reverse("pybb_post", args=[self.post.id])
        self.data = {"image": 0, "user": 0, "post": self.post.id}

    def test_regular_user_can_react(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Reaction.objects.filter(post=self.post, user=self.regular_user).exists()
        )

    def test_anonymous_reaction_redirects_to_login(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertFalse(Reaction.objects.exists())

    def test_no_reaction_on_hidden_post(self):
        self.post.hidden = True
        self.post.save()
        self.client.force_login(self.regular_user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Reaction.objects.exists())

    def test_no_reaction_on_internal_post(self):
        self.category.internal = True
        self.category.save()
        self.client.force_login(self.regular_user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Reaction.objects.exists())


class TestFeedsAndSitemap(_ForumTestBase):
    def setUp(self):
        super().setUp()
        self.other_forum = Forum.objects.create(category=self.category, name="Other")
        other_topic = Topic.objects.create(
            forum=self.other_forum, name="Other topic", user=self.regular_user
        )
        Post.objects.create(
            topic=other_topic,
            user=self.regular_user,
            body="Post in other forum",
            markup="markdown",
        )
        internal_category = Category.objects.create(name="Staff", internal=True)
        self.internal_forum = Forum.objects.create(
            category=internal_category, name="Secret staff forum"
        )

    def test_posts_feed_drops_topic_hidden_after_first_request(self):
        Post.objects.create(
            topic=self.topic,
            user=self.regular_user,
            body="Visible reply",
            markup="markdown",
        )
        url = reverse("pybb_feed_posts")
        self.assertContains(self.client.get(url), "Visible reply")
        head = self.topic.posts.first()
        head.hidden = True
        head.save()
        self.assertNotContains(self.client.get(url), "Visible reply")

    def test_forum_posts_feed_only_contains_that_forum(self):
        url = reverse("pybb_feed_posts", kwargs={"topic_id": self.forum.id})
        response = self.client.get(url)
        self.assertContains(response, "First post")
        self.assertNotContains(response, "Post in other forum")

    def test_internal_forum_has_no_feed(self):
        for name in ("pybb_feed_posts", "pybb_feed_topics"):
            url = reverse(name, kwargs={"topic_id": self.internal_forum.id})
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_sitemap_skips_internal_forums(self):
        self.assertNotIn(self.internal_forum, ForumSitemap().items())
        self.assertIn(self.forum, ForumSitemap().items())
