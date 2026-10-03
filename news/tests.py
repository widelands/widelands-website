from datetime import datetime, timedelta

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from news.models import Category, Post
from news.search_indexes import PostIndex


class UnpublishedNewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(title="Releases", slug="releases")
        last_week = datetime.now() - timedelta(days=7)
        cls.public = cls._post("Public news", status=2, publish=last_week)
        cls.draft = cls._post("Secret draft", status=1, publish=last_week)
        cls.scheduled = cls._post(
            "Scheduled news", status=2, publish=datetime.now() + timedelta(days=7)
        )
        cls.editor = User.objects.create_user("editor", password="pw")
        cls.editor.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="news", codename="change_post"
            )
        )

    @classmethod
    def _post(cls, title, status, publish):
        post = Post.objects.create(
            title=title,
            slug=title.lower().replace(" ", "-"),
            body=f"{title} body",
            status=status,
            publish=publish,
        )
        post.categories.add(cls.category)
        return post

    def _listing_urls(self):
        publish = self.public.publish
        return [
            reverse("news_index"),
            reverse("news_archive_year", args=(publish.year,)),
            reverse("news_archive_month", args=(publish.year, publish.strftime("%b"))),
            reverse("category_posts", args=(self.category.slug,)),
        ]

    def test_listings_hide_drafts_and_scheduled_posts(self):
        for url in self._listing_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Public news")
                self.assertNotContains(response, "Secret draft")
                self.assertNotContains(response, "Scheduled news")

    def test_detail_of_unpublished_posts_is_not_found(self):
        self.assertEqual(
            self.client.get(self.public.get_absolute_url()).status_code, 200
        )
        for post in (self.draft, self.scheduled):
            with self.subTest(post=post.title):
                response = self.client.get(post.get_absolute_url())
                self.assertEqual(response.status_code, 404)

    def test_news_editors_can_preview_unpublished_posts(self):
        self.client.force_login(self.editor)
        for post in (self.draft, self.scheduled):
            with self.subTest(post=post.title):
                response = self.client.get(post.get_absolute_url())
                self.assertContains(response, f"{post.title} body")

    def test_search_index_only_contains_published_posts(self):
        self.assertQuerySetEqual(PostIndex().index_queryset(), [self.public])
