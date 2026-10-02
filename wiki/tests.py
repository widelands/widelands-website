from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from wiki.models import Article


class _WikiTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.article = Article.objects.create(
            title="TestArticle",
            content="Some content",
            creator=self.user,
        )


class TestObserveArticleRequiresPost(_WikiTestBase):
    def test_get_rejected(self):
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_observe", args=[self.article.title])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_post_succeeds(self):
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_observe", args=[self.article.title])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)


class TestStopObservingArticleRequiresPost(_WikiTestBase):
    def test_get_rejected(self):
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_stop_observing", args=[self.article.title])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class TestArticleDiffPermission(_WikiTestBase):
    def test_public_article_diff_allowed(self):
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_preview_diff")
        response = self.client.post(
            url, {"article": self.article.pk, "body": "New content"}
        )
        self.assertEqual(response.status_code, 200)

    def test_group_article_diff_forbidden(self):
        """Articles scoped to a group should not be diffable via the AJAX endpoint."""
        from django.contrib.contenttypes.models import ContentType

        # Set a fake group reference on the article to simulate a group-scoped article.
        ct = ContentType.objects.get_for_model(User)
        self.article.content_type = ct
        self.article.object_id = self.user.pk
        self.article.save()

        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_preview_diff")
        response = self.client.post(
            url, {"article": self.article.pk, "body": "New content"}
        )
        self.assertEqual(response.status_code, 403)
