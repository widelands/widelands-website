from datetime import datetime, timedelta
from unittest import skipUnless

from django.contrib.auth.models import User
from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase
from django.urls import reverse
from django.utils.safestring import mark_safe

from news.models import Post as NewsPost
from pybb.models import Category, Forum, Post, Topic
from wiki.models import Article
from wlsearch.fulltext import SearchQuery
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

    def test_phrase_words_are_highlighted_and_excluded_words_not(self):
        snippet = EscapingHighlighter('"main page" -barbarians').highlight(
            "The main page of the barbarians"
        )
        self.assertEqual(
            snippet,
            '...<span class="highlighted">main</span> '
            '<span class="highlighted">page</span> of the barbarians',
        )

    def test_words_beginning_with_a_query_word_or_its_stem_are_highlighted(self):
        snippet = EscapingHighlighter("mining").highlight("Mines determine mining")
        self.assertEqual(
            snippet,
            '<span class="highlighted">Mines</span> determine '
            '<span class="highlighted">mining</span>',
        )


class TestSearchQuery(SimpleTestCase):
    def boolean_mode(self, query, ignored=()):
        return SearchQuery(query).boolean_mode(lambda word: word in ignored)

    def test_words_phrases_and_exclusions(self):
        self.assertEqual(
            self.boolean_mode('mine "main page" std::vector -barbarian -"big hut"'),
            '+mine* +"main page" +"std vector" -barbarian* -"big hut"',
        )

    def test_operators_in_the_query_are_not_passed_on(self):
        self.assertEqual(
            self.boolean_mode('+a* (b) @3 ~c <d >e "f -'),
            '+a* +b* +3* +c* +d* +e* +"f"',
        )

    def test_words_also_match_by_their_stem(self):
        self.assertEqual(
            self.boolean_mode("Mining buildings settings -Barbarians"),
            "+(mining* mine*) +build* +settings* -barbarian*",
        )

    def test_words_missing_from_the_index_are_left_out(self):
        self.assertEqual(
            self.boolean_mode('the mines -of "of the" "the hut"', {"the", "of"}),
            '+mine* +"the hut"',
        )

    def test_nothing_to_search_for(self):
        self.assertEqual(self.boolean_mode("the -mines", {"the"}), "")
        self.assertEqual(self.boolean_mode('- "" -mines'), "")


class _SearchTestBase(TransactionTestCase):
    # MariaDB's FULLTEXT indexes only contain committed rows
    serialized_rollback = True

    def setUp(self):
        self.user = User.objects.create_user(username="mallory", password="pass")

    def search(self, **params):
        response = self.client.get(reverse("search"), params)
        self.assertEqual(response.status_code, 200)
        return response


class _ForumSearchTestBase(_SearchTestBase):
    def setUp(self):
        super().setUp()
        category = Category.objects.create(name="General")
        self.forum = Forum.objects.create(category=category, name="Forum")
        self.topic = Topic.objects.create(
            forum=self.forum, name="Topic", user=self.user
        )

    def post(self, body, **kwargs):
        return Post.objects.create(
            topic=self.topic, user=self.user, markup="markdown", body=body, **kwargs
        )

    def found_posts(self, **params):
        response = self.search(incl_forum="on", **params)
        return {post.body for post in response.context["result"].get("posts", [])}


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

        response = self.search(q="zzqxwiki", incl_wiki="on")

        self.assertSnippetEscaped(response, "zzqxwiki", "<img src=x onerror=alert(2)//")

    def test_news_post(self):
        NewsPost.objects.create(
            title="News",
            slug="news",
            author=self.user,
            body="zzqxnews\n\n<script><img src=x onerror=alert(3)//</script>\n",
            publish=datetime.now() - timedelta(days=1),
        )

        response = self.search(q="zzqxnews", incl_news="on")

        self.assertSnippetEscaped(response, "zzqxnews", "<img src=x onerror=alert(3)//")


class TestSearchTerms(_ForumSearchTestBase):
    def setUp(self):
        super().setUp()
        self.post("zzqx mines of the barbarians")
        self.post("zzqx main page")
        self.post("zzqx page about the main road")

    def test_all_words_must_match(self):
        self.assertEqual(
            self.found_posts(q="zzqx barbarians"), {"zzqx mines of the barbarians"}
        )

    def test_words_match_other_forms_of_the_word(self):
        for query in ("mine", "mining", "Barbarian"):
            with self.subTest(query=query):
                self.assertEqual(
                    self.found_posts(q=query), {"zzqx mines of the barbarians"}
                )

    def test_phrases_match_exactly(self):
        self.assertEqual(self.found_posts(q='"main page"'), {"zzqx main page"})

    def test_excluded_words_must_not_match(self):
        self.assertEqual(
            self.found_posts(q="zzqx -barbarians -road"), {"zzqx main page"}
        )

    @skipUnless(connection.vendor == "mysql", "FULLTEXT stopwords")
    def test_words_missing_from_the_index_are_ignored(self):
        self.assertEqual(
            self.found_posts(q="the barbarians"), {"zzqx mines of the barbarians"}
        )


class TestForumSearch(_ForumSearchTestBase):
    def test_start_date(self):
        self.post("zzqx old", created=datetime.now() - timedelta(days=400))
        self.post("zzqx new")

        self.assertEqual(
            self.found_posts(q="zzqx", start_date="2000-01-01"),
            {"zzqx old", "zzqx new"},
        )
        last_month = (datetime.now() - timedelta(days=30)).date().isoformat()
        self.assertEqual(
            self.found_posts(q="zzqx", start_date=last_month), {"zzqx new"}
        )

    def test_hidden_posts_are_not_found(self):
        self.post("zzqx visible")
        self.post("zzqx spam", hidden=True)

        self.assertEqual(self.found_posts(q="zzqx"), {"zzqx visible"})

    def test_topics_are_found_by_name(self):
        Topic.objects.create(forum=self.forum, name="Zzqx topic", user=self.user)

        response = self.search(q="zzqx", incl_forum="on")

        topics = response.context["result"]["topics"]
        self.assertEqual([topic.name for topic in topics], ["Zzqx topic"])


class TestDeletedWikiArticles(_SearchTestBase):
    def test_deleted_article_is_not_found(self):
        Article.objects.create(title="Kept", creator=self.user, content="zzqxwiki")
        Article.objects.create(
            title="Gone", creator=self.user, content="zzqxwiki", deleted=True
        )

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
