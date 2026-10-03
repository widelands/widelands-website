from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from django.utils import timezone

from check_input.models import SuspiciousInput, SuspiciousKeyword
from news.models import Post
from threadedcomments.models import DEFAULT_MAX_COMMENT_DEPTH, ThreadedComment


class CommentViewTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.post = Post.objects.create(
            title="News",
            slug="news",
            author=self.author,
            body="Body",
            publish=timezone.now(),
        )
        self.other_post = Post.objects.create(
            title="Other",
            slug="other",
            author=self.author,
            body="Body",
            publish=timezone.now(),
        )
        self.ct = ContentType.objects.get_for_model(Post)
        self.comment = ThreadedComment.objects.create(
            content_type=self.ct,
            object_id=self.post.pk,
            user=self.author,
            comment="original",
        )

    def _reply_url(self, post, parent=None):
        kwargs = {"content_type": self.ct.id, "object_id": post.pk}
        if parent is None:
            return reverse("tc_comment", kwargs=kwargs)
        return reverse("tc_comment_parent", kwargs=dict(kwargs, parent_id=parent.id))

    def _edit(self, user):
        self.client.login(username=user.username, password="pass")
        return self.client.post(
            reverse("tc_comment_edit", kwargs={"edit_id": self.comment.id}),
            {"comment": "edited", "markup": 1, "next": "/news/"},
        )

    def test_other_user_cannot_edit_comment(self):
        response = self._edit(self.other)
        self.assertEqual(response.status_code, 404)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, "original")
        self.assertEqual(self.comment.user, self.author)

    def test_author_can_edit_comment(self):
        response = self._edit(self.author)
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, "edited")
        self.assertEqual(self.comment.user, self.author)

    def test_reply_to_comment(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(
            self._reply_url(self.post, self.comment),
            {"comment": "reply", "markup": 1, "next": "/news/"},
        )
        self.assertEqual(response.status_code, 302)
        reply = ThreadedComment.objects.get(comment="reply")
        self.assertEqual(reply.parent, self.comment)
        self.assertEqual(reply.user, self.other)

    def test_parent_of_other_object_rejected(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(
            self._reply_url(self.other_post, self.comment),
            {"comment": "reply", "markup": 1, "next": "/news/"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(ThreadedComment.objects.filter(comment="reply").exists())

    def test_nonexistent_target_rejected(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(
            reverse(
                "tc_comment", kwargs={"content_type": self.ct.id, "object_id": 99999}
            ),
            {"comment": "orphan", "markup": 1, "next": "/news/"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(ThreadedComment.objects.filter(comment="orphan").exists())

    def test_nesting_is_capped(self):
        parent = self.comment
        for depth in range(1, DEFAULT_MAX_COMMENT_DEPTH):
            parent = ThreadedComment.objects.create(
                content_type=self.ct,
                object_id=self.post.pk,
                user=self.author,
                comment=f"depth {depth}",
                parent=parent,
            )
        self.client.login(username="other", password="pass")
        response = self.client.post(
            self._reply_url(self.post, parent),
            {"comment": "too deep", "markup": 1, "next": "/news/"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ThreadedComment.objects.filter(comment="too deep").exists())
        # One level less is still fine.
        response = self.client.post(
            self._reply_url(self.post, parent.parent),
            {"comment": "deep", "markup": 1, "next": "/news/"},
        )
        self.assertEqual(response.status_code, 302)

    def test_offsite_next_ignored(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(
            self._reply_url(self.post) + "?next=/news/",
            {"comment": "hi", "markup": 1, "next": "https://evil.example/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/news/")

    def test_deep_tree_renders(self):
        parent = self.comment
        for depth in range(1, 1500):
            parent = ThreadedComment(
                content_type=self.ct,
                object_id=self.post.pk,
                user=self.author,
                comment=f"depth {depth}",
                parent=parent,
            )
            parent.save()
        tree = ThreadedComment.public.get_tree(self.post)
        self.assertEqual(len(tree), 1500)
        self.assertEqual(tree[-1].depth, 1499)


@override_settings(MAX_HIDDEN_POSTS=2)
class CommentSpamCheckTestCase(TestCase):
    def setUp(self):
        SuspiciousKeyword.objects.create(keyword="spamword")
        self.user = User.objects.create_user(username="user", password="pass")
        self.post = Post.objects.create(
            title="News",
            slug="news",
            author=self.user,
            body="Body",
            publish=timezone.now(),
        )
        self.url = reverse(
            "tc_comment",
            kwargs={
                "content_type": ContentType.objects.get_for_model(Post).id,
                "object_id": self.post.pk,
            },
        )
        self.client.login(username="user", password="pass")

    def _comment(self, text, url=None):
        return self.client.post(
            url or self.url, {"comment": text, "markup": 1, "next": "/news/"}
        )

    def test_spam_comment_is_hidden_and_recorded(self):
        response = self._comment("buy spamword now")
        self.assertRedirects(
            response, reverse("found_spam"), fetch_redirect_response=False
        )
        comment = ThreadedComment.objects.get()
        self.assertFalse(comment.is_public)
        flagged = SuspiciousInput.objects.get()
        self.assertEqual(flagged.content_object, comment)
        self.assertEqual(flagged.user, self.user)
        self.assertEqual(ThreadedComment.public.get_tree(self.post), [])
        self.assertEqual(ThreadedComment.public.all_for_object(self.post).count(), 0)

    def test_clean_comment_is_published(self):
        response = self._comment("nice news")
        self.assertRedirects(response, "/news/", fetch_redirect_response=False)
        comment = ThreadedComment.objects.get()
        self.assertTrue(comment.is_public)
        self.assertEqual(ThreadedComment.public.get_tree(self.post), [comment])
        self.assertFalse(SuspiciousInput.objects.exists())

    def test_spam_edit_hides_comment(self):
        self._comment("nice news")
        comment = ThreadedComment.objects.get()
        response = self._comment(
            "now with spamword",
            url=reverse("tc_comment_edit", kwargs={"edit_id": comment.id}),
        )
        self.assertRedirects(
            response, reverse("found_spam"), fetch_redirect_response=False
        )
        comment.refresh_from_db()
        self.assertEqual(comment.comment, "now with spamword")
        self.assertFalse(comment.is_public)

    def test_spam_comments_lock_out_user(self):
        self._comment("spamword one")
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self._comment("spamword two")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
