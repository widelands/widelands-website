from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.redirects.models import Redirect
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

    def test_anonymous_diff_denied(self):
        url = reverse("wiki_preview_diff")
        response = self.client.post(url, {"article": self.article.pk, "body": ""})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("Some content", response.content.decode())

    def test_deleted_article_diff_not_found(self):
        self.article.deleted = True
        self.article.save()
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_preview_diff")
        response = self.client.post(url, {"article": self.article.pk, "body": ""})
        self.assertEqual(response.status_code, 404)

    def test_deleted_article_diff_allowed_for_staff(self):
        """Staff edit deleted articles in the trash, which uses the diff."""
        self.user.is_staff = True
        self.user.save()
        self.article.deleted = True
        self.article.save()
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_preview_diff")
        response = self.client.post(url, {"article": self.article.pk, "body": ""})
        self.assertEqual(response.status_code, 200)


class TestEditArticleStaffFields(_WikiTestBase):
    def _post_edit(self, url_name, **extra):
        data = {
            "title": self.article.title,
            "content": "Edited content",
            "summary": "Summary",
            "comment": "",
            "action": "edit",
        }
        data.update(extra)
        return self.client.post(reverse(url_name, args=[self.article.title]), data)

    def _make_staff(self):
        self.user.is_staff = True
        self.user.save()

    def test_non_staff_cannot_delete_or_redirect(self):
        self.client.login(username="testuser", password="pass")
        response = self._post_edit(
            "wiki_edit", deleted="on", redirect_to="https://evil.example/"
        )
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Edited content")
        self.assertFalse(self.article.deleted)
        self.assertFalse(Redirect.objects.exists())

    def test_staff_can_delete_and_redirect(self):
        self._make_staff()
        self.client.login(username="testuser", password="pass")
        response = self._post_edit(
            "wiki_edit", deleted="on", redirect_to="/documentation/"
        )
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertTrue(self.article.deleted)
        redirect = Redirect.objects.get(old_path=self.article.get_absolute_url())
        self.assertEqual(redirect.new_path, "/documentation/")

    def test_non_staff_cannot_edit_deleted_article(self):
        # The gone page shows the last editor, so the article needs a revision
        self.article.new_revision("", self.article.title, "Created", self.user)
        self.article.deleted = True
        self.article.save()
        self.client.login(username="testuser", password="pass")
        response = self._post_edit("wiki_edit")
        self.assertEqual(response.status_code, 410)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Some content")

    def test_non_staff_trash_edit_forbidden(self):
        self.article.deleted = True
        self.article.save()
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_edit_deleted", args=[self.article.title])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("Some content", response.content.decode())
        response = self._post_edit("wiki_edit_deleted")
        self.assertEqual(response.status_code, 403)
        self.article.refresh_from_db()
        self.assertTrue(self.article.deleted)
        self.assertEqual(self.article.content, "Some content")

    def test_staff_can_undelete_in_trash(self):
        self._make_staff()
        self.article.deleted = True
        self.article.save()
        self.client.login(username="testuser", password="pass")
        url = reverse("wiki_edit_deleted", args=[self.article.title])
        response = self.client.get(url)
        self.assertContains(response, "Some content")
        response = self._post_edit("wiki_edit_deleted")
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertFalse(self.article.deleted)

    def test_group_fields_are_ignored(self):
        """The group of an article cannot be set through the form."""
        ct = ContentType.objects.get_for_model(ContentType)
        self.client.login(username="testuser", password="pass")
        response = self._post_edit("wiki_edit", content_type=ct.pk, object_id=ct.pk)
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Edited content")
        self.assertIsNone(self.article.content_type)
        self.assertIsNone(self.article.object_id)
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)
        url = reverse("wiki_article_history", args=[self.article.title])
        self.assertEqual(self.client.get(url).status_code, 200)


class TestRevertToRevision(_WikiTestBase):
    def setUp(self):
        super().setUp()
        self.article.new_revision("", self.article.title, "Created", self.user)
        self.article.content = "Changed content"
        self.article.save()
        self.article.new_revision("Some content", self.article.title, "", self.user)
        self.client.login(username="testuser", password="pass")

    def _revert(self, revision=1):
        url = reverse("wiki_revert_to_revision", args=[self.article.title])
        return self.client.post(url, {"revision": revision})

    def test_revert(self):
        response = self._revert()
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Some content")

    def test_unknown_revision_not_found(self):
        response = self._revert(revision=5)
        self.assertEqual(response.status_code, 404)

    def test_non_staff_cannot_revert_deleted_article(self):
        self.article.deleted = True
        self.article.save()
        response = self._revert()
        self.assertEqual(response.status_code, 404)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Changed content")

    def test_staff_can_revert_deleted_article(self):
        self.user.is_staff = True
        self.user.save()
        self.article.deleted = True
        self.article.save()
        response = self._revert()
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Some content")


class TestBacklinks(_WikiTestBase):
    def test_deleted_articles_are_not_listed(self):
        Article.objects.create(title="LinkingArticle", content="[[ TestArticle ]]")
        Article.objects.create(
            title="DeletedArticle", content="[[ TestArticle ]]", deleted=True
        )
        response = self.client.get(reverse("backlinks", args=[self.article.title]))
        self.assertContains(response, "LinkingArticle")
        self.assertNotContains(response, "DeletedArticle")
