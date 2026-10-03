from django import forms
from django.contrib.auth.models import User
from django.template import Context
from django.template import Template
from django.test import SimpleTestCase
from django.test import TestCase
from django.urls import reverse

from tagging.models import Tag
from tagging.models import TaggedItem
from tagging.utils import edit_string_for_tags
from tagging.utils import parse_tag_input
from wiki.models import Article


class TestParseTagInput(SimpleTestCase):
    def test_space_delimited(self):
        self.assertEqual(parse_tag_input("one two  one"), ["one", "two"])

    def test_loose_commas_delimit_multiple_words(self):
        self.assertEqual(parse_tag_input("one two, three"), ["one two", "three"])

    def test_quotes_may_contain_commas(self):
        self.assertEqual(parse_tag_input('"one, two" three'), ["one, two", "three"])

    def test_unclosed_quote_is_treated_as_unquoted(self):
        self.assertEqual(parse_tag_input('one "two three'), ["one", "three", "two"])

    def test_empty(self):
        self.assertEqual(parse_tag_input(""), [])
        self.assertEqual(parse_tag_input(None), [])

    def test_edit_string_round_trips(self):
        for names in (["one", "two"], ["one two", "three"], ["a, b", "c"], ["x y"]):
            tags = [Tag(name=name) for name in names]
            self.assertEqual(parse_tag_input(edit_string_for_tags(tags)), names)


class TestArticleTags(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tagger", password="pass")
        self.article = Article.objects.create(
            title="Tagged", content="x", creator=self.user, tags="Foo bar"
        )
        self.other = Article.objects.create(
            title="Other", content="x", creator=self.user, tags="bar"
        )

    def tag_names(self, article):
        return [tag.name for tag in Tag.objects.get_for_object(article)]

    def test_tags_are_saved_lowercase(self):
        self.assertEqual(self.tag_names(self.article), ["bar", "foo"])
        self.assertEqual(Article.objects.get(pk=self.article.pk).tags, "foo bar")

    def test_updating_tags_removes_and_adds_items(self):
        self.article.tags = "foo baz"
        self.article.save()
        self.assertEqual(self.tag_names(self.article), ["baz", "foo"])
        self.assertEqual(self.tag_names(self.other), ["bar"])

    def test_deleting_tags_clears_them(self):
        del self.article.tags
        self.article.save(update_fields=["tags"])
        self.assertEqual(self.tag_names(self.article), [])
        self.assertFalse(TaggedItem.objects.filter(object_id=self.article.pk).exists())

    def test_form_field_rejects_overlong_tags(self):
        class ArticleForm(forms.ModelForm):
            class Meta:
                model = Article
                fields = ["tags"]

        self.assertTrue(ArticleForm({"tags": "a" * 20}).is_valid())
        self.assertIn("tags", ArticleForm({"tags": "a" * 21}).errors)

    def test_tags_for_object_template_tag(self):
        template = Template(
            "{% load tagging_tags %}{% tags_for_object article as tags %}"
            "{% for tag in tags %}{{ tag.name }};{% endfor %}"
        )
        rendered = template.render(Context({"article": self.article}))
        self.assertEqual(rendered, "bar;foo;")

    def test_tag_list_shows_only_tagged_live_articles(self):
        deleted = Article.objects.create(
            title="Gone", content="x", creator=self.user, tags="bar", deleted=True
        )
        response = self.client.get(reverse("article_tag_detail", args=["bar"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tag"].name, "bar")
        self.assertEqual(
            list(response.context["object_list"]), [self.other, self.article]
        )
        self.assertNotContains(response, deleted.title)

        response = self.client.get(reverse("article_tag_detail", args=["foo"]))
        self.assertEqual(list(response.context["object_list"]), [self.article])

    def test_tag_list_unknown_tag_is_404(self):
        response = self.client.get(reverse("article_tag_detail", args=["nope"]))
        self.assertEqual(response.status_code, 404)
