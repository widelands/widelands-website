import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from haystack import connections

from news.models import Post as NewsPost
from pybb.models import Category, Forum, Post, Topic
from wiki.models import Article
from wlsearch.highlighting import EscapingHighlighter


class TestEscapingHighlighter(SimpleTestCase):
    def test_plain_text_is_escaped(self):
        snippet = EscapingHighlighter("word more").highlight(
            "word <img src=x onerror=alert(1)// & more"
        )
        self.assertEqual(
            snippet,
            '<span class="highlighted">word</span> '
            "&lt;img src=x onerror=alert(1)// &amp; "
            '<span class="highlighted">more</span>',
        )

    def test_html_is_converted_to_text(self):
        snippet = EscapingHighlighter("word").highlight(
            mark_safe("<p><em>Word</em> &amp; &lt;b&gt;</p>")
        )
        self.assertEqual(
            snippet, '<span class="highlighted">Word</span> &amp; &lt;b&gt;'
        )

    def test_window_is_cut_with_ellipses(self):
        snippet = EscapingHighlighter("word", max_length=10).highlight(
            "<<<<< word <<<<<<<<"
        )
        self.assertEqual(
            snippet, '...<span class="highlighted">word</span> &lt;&lt;&lt;&lt;&lt;...'
        )


class _SearchTestBase(TestCase):
    """Searches a Whoosh index in a temporary directory."""

    def setUp(self):
        index_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, index_dir)
        patcher = mock.patch.dict(
            connections.connections_info["default"], {"PATH": index_dir}
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        connections.reload("default")
        self.addCleanup(connections.reload, "default")
        self.user = User.objects.create_user(username="mallory", password="pass")

    def rebuild_index(self):
        call_command("rebuild_index", interactive=False, verbosity=0)

    def search(self, **params):
        response = self.client.get(reverse("search"), params)
        self.assertEqual(response.status_code, 200)
        return response


class TestSearchSnippetsAreEscaped(_SearchTestBase):
    def assertSnippetEscaped(self, response, query, payload):
        self.assertContains(response, f'<span class="highlighted">{query}</span>')
        self.assertNotContains(response, payload)
        self.assertContains(response, payload.replace("<", "&lt;"))

    def test_forum_post(self):
        category = Category.objects.create(name="General")
        forum = Forum.objects.create(category=category, name="Forum")
        topic = Topic.objects.create(forum=forum, name="Topic", user=self.user)
        Post.objects.create(
            topic=topic,
            user=self.user,
            markup="markdown",
            body="zzqxforum `<img src=x onerror=alert(1)//`",
        )
        self.rebuild_index()

        response = self.search(q="zzqxforum", incl_forum="on")

        self.assertSnippetEscaped(
            response, "zzqxforum", "<img src=x onerror=alert(1)//"
        )

    def test_wiki_article(self):
        Article.objects.create(
            title="Zzqx",
            creator=self.user,
            content="zzqxwiki\n\n<script><img src=x onerror=alert(2)//</script>\n",
        )
        self.rebuild_index()

        response = self.search(q="zzqxwiki", incl_wiki="on")

        self.assertSnippetEscaped(response, "zzqxwiki", "<img src=x onerror=alert(2)//")

    def test_news_post(self):
        NewsPost.objects.create(
            title="News",
            slug="news",
            author=self.user,
            body="zzqxnews\n\n<script><img src=x onerror=alert(3)//</script>\n",
            publish=timezone.now() - timedelta(days=1),
        )
        self.rebuild_index()

        response = self.search(q="zzqxnews", incl_news="on")

        self.assertSnippetEscaped(response, "zzqxnews", "<img src=x onerror=alert(3)//")


class TestDeletedWikiArticles(_SearchTestBase):
    def setUp(self):
        super().setUp()
        Article.objects.create(title="Kept", creator=self.user, content="zzqxwiki")
        self.deleted = Article.objects.create(
            title="Gone", creator=self.user, content="zzqxwiki"
        )

    def test_deleted_article_is_not_indexed(self):
        self.deleted.deleted = True
        self.deleted.save()
        self.rebuild_index()

        response = self.search(q="zzqxwiki", incl_wiki="on")

        self.assertContains(response, "Kept")
        self.assertNotContains(response, "Gone")

    def test_article_deleted_after_indexing_is_not_shown(self):
        self.rebuild_index()
        self.deleted.deleted = True
        self.deleted.save()

        response = self.search(q="zzqxwiki", incl_wiki="on")

        self.assertContains(response, "Kept")
        self.assertNotContains(response, "Gone")


class TestSearchResultPages(_SearchTestBase):
    def setUp(self):
        super().setUp()
        # Not a multiple of the page size, so the last page is a short one
        Article.objects.bulk_create(
            Article(title=f"Article{i}", creator=self.user, content="zzqxwiki")
            for i in range(70)
        )
        self.rebuild_index()

    def titles(self, response):
        return {result.title for result in response.context["result"]["wiki"]}

    def test_results_are_split_into_pages(self):
        first = self.search(q="zzqxwiki", incl_wiki="on")
        second = self.search(q="zzqxwiki", incl_wiki="on", page=2)

        self.assertEqual(len(self.titles(first)), 50)
        self.assertEqual(len(self.titles(second)), 20)
        self.assertEqual(
            self.titles(first) | self.titles(second),
            {f"Article{i}" for i in range(70)},
        )
        self.assertContains(first, "page=2")
        self.assertContains(second, "page=1")

    def test_pages_out_of_range_show_nothing(self):
        for page in (3, 0, "x"):
            response = self.search(q="zzqxwiki", incl_wiki="on", page=page)
            self.assertNotIn("wiki", response.context["result"])
