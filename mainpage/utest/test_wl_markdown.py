#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: utests/test_wl_markdown.py
#
# Created by Holger Rapp on 2009-02-28.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

# Since we want to include something from one path up,
# we append the parent path to sys.path
import sys

sys.path.append("..")

import unittest
from wiki.models import Article
from django.test import TestCase as DBTestCase

from ..templatetags.wl_markdown import do_wl_markdown


class TestWlMarkdown(DBTestCase):
    def setUp(self):
        a = Article.objects.create(title="MainPage")
        a = Article.objects.create(title="HalloWelt")
        a = Article.objects.create(title="NoWikiWord")
        a = Article.objects.create(title="WikiWord")

    def _check(self, input, wanted):
        res = do_wl_markdown(input)
        self.assertEqual(wanted, res)

    def test_simple_case__correct_result(self):
        input = "Hallo Welt"
        wanted = "<p>Hallo Welt</p>"
        self._check(input, wanted)

    # Existing links
    def test_existing_link_html(self):
        input = """<a href="/wiki/MainPage">this page</a>"""
        wanted = """<p><a href="/wiki/MainPage">this page</a></p>"""
        self._check(input, wanted)

    def test_existing_link_markdown(self):
        input = """[this page](/wiki/MainPage)"""
        wanted = """<p><a href="/wiki/MainPage">this page</a></p>"""
        self._check(input, wanted)

    def test_existing_editlink_wikiword(self):
        input = """<a href="/wiki/MainPage/edit/">this page</a>"""
        wanted = """<p><a href="/wiki/MainPage/edit/">this page</a></p>"""
        self._check(input, wanted)

    # Missing links
    def test_missing_link_html(self):
        input = """<a href="/wiki/MissingPage">this page</a>"""
        wanted = """<p><a class="missingLink" href="/wiki/MissingPage" title="This Link is misspelled or missing. Click to create it anyway.">this page</a></p>"""
        self._check(input, wanted)

    def test_missing_link_markdown(self):
        input = """[this page](/wiki/MissingPage)"""
        wanted = """<p><a class="missingLink" href="/wiki/MissingPage" title="This Link is misspelled or missing. Click to create it anyway.">this page</a></p>"""
        self._check(input, wanted)

    def test_missing_editlink_wikiword(self):
        input = """<a href="/wiki/MissingPage/edit/">this page</a>"""
        wanted = """<p><a class="missingLink" href="/wiki/MissingPage/edit/" title="This Link is misspelled or missing. Click to create it anyway.">this page</a></p>"""
        self._check(input, wanted)

    # Check smileys
    def test_smiley_angel(self):
        input = """O:-)"""
        wanted = (
            """<p><img alt="O:-)" src="/static/img/smileys/face-angel.png"/> </p>"""
        )
        self._check(input, wanted)

    def test_smiley_crying(self):
        input = """:'-("""
        wanted = (
            """<p><img alt=":'-(" src="/static/img/smileys/face-crying.png"/> </p>"""
        )
        self._check(input, wanted)

    def test_smiley_glasses(self):
        input = """8-)"""
        wanted = (
            """<p><img alt="8-)" src="/static/img/smileys/face-glasses.png"/> </p>"""
        )
        self._check(input, wanted)

    def test_smiley_kiss(self):
        input = """:-x"""
        wanted = """<p><img alt=":-x" src="/static/img/smileys/face-kiss.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_plain(self):
        input = """:-|"""
        wanted = """<p><img alt=":-|" src="/static/img/smileys/face-plain.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_sad(self):
        input = """:-("""
        wanted = """<p><img alt=":-(" src="/static/img/smileys/face-sad.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_smilebig(self):
        input = """:))"""
        wanted = (
            """<p><img alt=":))" src="/static/img/smileys/face-smile-big.png"/> </p>"""
        )
        self._check(input, wanted)

    def test_smiley_smile(self):
        input = """:-)"""
        wanted = """<p><img alt=":-)" src="/static/img/smileys/face-smile.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_surprise(self):
        input = """:-O"""
        wanted = (
            """<p><img alt=":-O" src="/static/img/smileys/face-surprise.png"/> </p>"""
        )
        self._check(input, wanted)

    def test_smiley_wink(self):
        input = """;-)"""
        wanted = """<p><img alt=";-)" src="/static/img/smileys/face-wink.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_grin(self):
        input = """:D"""
        wanted = """<p><img alt=":D" src="/static/img/smileys/face-grin.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_sad(self):
        input = """:("""
        wanted = """<p><img alt=":(" src="/static/img/smileys/face-sad.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_smile(self):
        input = """:)"""
        wanted = """<p><img alt=":)" src="/static/img/smileys/face-smile.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_surprise(self):
        input = """:O"""
        wanted = """<p><img alt=":O" src="/static/img/smileys/face-shock.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_wink(self):
        input = """;)"""
        wanted = """<p><img alt=";)" src="/static/img/smileys/face-wink.png"/> </p>"""
        self._check(input, wanted)

    def test_smiley_monkey(self):
        input = """:(|)"""
        wanted = (
            """<p><img alt=":(|)" src="/static/img/smileys/face-monkey.png"/> </p>"""
        )
        self._check(input, wanted)

    # Occured errors
    def test_wiki_rootlink(self):
        input = """<a href="/wiki">this page</a>"""
        wanted = """<p><a href="/wiki">this page</a></p>"""
        self._check(input, wanted)

    def test_wiki_rootlink_with_slash(self):
        input = """<a href="/wiki/">this page</a>"""
        wanted = """<p><a class="wrongLink" href="/wiki/" title="This Link misses an articlename">this page</a></p>"""
        self._check(input, wanted)

    # Special pages
    def test_wiki_specialpage(self):
        input = """<a href="/wiki/list">this page</a>"""
        wanted = """<p><a class="specialLink" href="/wiki/list">this page</a></p>"""
        self._check(input, wanted)

    def test_wiki_specialpage_markdown(self):
        input = """[list](/wiki/list)"""
        wanted = """<p><a class="specialLink" href="/wiki/list">list</a></p>"""
        self._check(input, wanted)

    # Special problem with emphasis
    def test_markdown_emphasis_problem(self):
        input = """*This is bold*  _This too_\n\n"""
        wanted = """<p><em>This is bold</em> <em>This too</em></p>"""
        self._check(input, wanted)

    # Another markdown problem with alt tag escaping
    def test_markdown_alt_problem(self):
        # {{{ Test strings
        input = """![img_thisisNOTitalicplease_name.png](/wlmedia/blah.png)\n\n"""
        wanted = '<p><img alt="img_thisisNOTitalicplease_name.png" src="/wlmedia/blah.png"/></p>'
        # }}}
        self._check(input, wanted)

    def test_emptystring_problem(self):
        # {{{ Test strings
        input = ""
        wanted = ""
        # }}}
        self._check(input, wanted)

    # Damned problem with tables
    def test_markdown_table_problem(self):
        # {{{ Test strings
        input = """
Header1 | Header 2
------- | --------
Value 1 | Value 2
Value 3 | Value 4
"""
        wanted = """<table>
<thead>
<tr>
<th>Header1</th>
<th>Header 2</th>
</tr>
</thead>
<tbody>
<tr>
<td>Value 1</td>
<td>Value 2</td>
</tr>
<tr>
<td>Value 3</td>
<td>Value 4</td>
</tr>
</tbody>
</table>"""
        # }}}
        self._check(input, wanted)


class TestWlMarkdownSanitized(DBTestCase):
    def assertSanitized(self, cases):
        for value, wanted in cases:
            with self.subTest(value=value):
                res = do_wl_markdown(value, "bleachit", beautify=False)
                self.assertEqual(res, wanted)

    def test_raw_script_block_stays_escaped(self):
        res = do_wl_markdown("Before\n\n<script>alert(1)</script>\n\nAfter", "bleachit")
        self.assertNotIn("<script", res)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", res)

    def test_smiley_and_entities_next_to_escaped_text(self):
        res = do_wl_markdown("<iframe src=x></iframe>\n\na < b & c :)", "bleachit")
        self.assertEqual(
            res,
            '&lt;iframe src=x&gt;&lt;/iframe&gt;\n\n<p>a &lt; b &amp; c <img alt=":)" '
            'src="/static/img/smileys/face-smile.png"/> </p>',
        )

    def test_collapsible_and_definition_list_tags_are_kept(self):
        res = do_wl_markdown(
            "<details><summary>Spoiler</summary>hidden</details>\n\n"
            "<dl><dt>Term</dt><dd>Definition</dd></dl>",
            "bleachit",
        )
        self.assertIn("<details><summary>Spoiler</summary>hidden</details>", res)
        self.assertIn("<dl><dt>Term</dt><dd>Definition</dd></dl>", res)

    def test_unsafe_attributes_and_url_schemes_are_removed(self):
        self.assertSanitized(
            [
                ("<img src=x onerror=alert(1)>", '<p><img src="x"/></p>'),
                (
                    "[x](javascript:alert(1)) "
                    '<a href="JaVaScRiPt:alert(1)">y</a> '
                    '<a href="&#106;avascript:alert(1)">z</a>',
                    "<p><a>x</a> <a>y</a> <a>z</a></p>",
                ),
                (
                    '<img src="data:image/svg+xml;base64,PHN2Zz4=" alt="d">',
                    '<p><img alt="d"/></p>',
                ),
                (
                    '<p style="background:url(x)" class="c" id="i" title="t">s</p>',
                    '<p class="c" id="i" title="t">s</p>',
                ),
                (
                    '<a href="/wiki/Foo" onclick="alert(1)">wiki</a> '
                    '<a href="mailto:a@b.c">mail</a> <a href="ftp://x/y">ftp</a>',
                    '<p><a href="/wiki/Foo">wiki</a> <a href="mailto:a@b.c">mail</a> '
                    "<a>ftp</a></p>",
                ),
            ]
        )

    def test_disallowed_tags_are_shown_as_text(self):
        self.assertSanitized(
            [
                (
                    "Saves are in C:/Documents and Settings/<Username>/.widelands",
                    "<p>Saves are in C:/Documents and Settings/&lt;Username&gt;"
                    "/.widelands</p>",
                ),
                (
                    "clear(boost::shared_ptr<Widelands::Pathfields> const&) <grin>",
                    "<p>clear(boost::shared_ptr&lt;Widelands::Pathfields&gt; "
                    "const&amp;) &lt;grin&gt;</p>",
                ),
                (
                    "<SCRIPT>alert(1)</SCRIPT> <script/x>alert(1)</script>",
                    "&lt;SCRIPT&gt;alert(1)&lt;/SCRIPT&gt;\n"
                    "<p>&lt;script/x&gt;alert(1)&lt;/script&gt;\n</p>",
                ),
                (
                    "<scr<script>ipt>alert(1)</script>",
                    "<p>&lt;scr&lt;script&gt;ipt&gt;alert(1)&lt;/script&gt;</p>",
                ),
                (
                    "```\n<b>not bold</b>\n```",
                    "<pre><code>&lt;b&gt;not bold&lt;/b&gt;\n</code></pre>",
                ),
            ]
        )

    def test_markup_cannot_be_smuggled_through_parser_quirks(self):
        self.assertSanitized(
            [
                (
                    "<svg><script>alert(1)</script></svg>",
                    "<p>&lt;svg&gt;&lt;script&gt;alert(1)&lt;/script&gt;&lt;/svg&gt;</p>",
                ),
                (
                    "<math><mi><mglyph><style><img src=x onerror=alert(1)>"
                    "</style></mglyph></mi></math>",
                    "&lt;math&gt;&lt;mi&gt;&lt;mglyph&gt;&lt;style&gt;"
                    '<img src="x"/>&lt;/style&gt;&lt;/mglyph&gt;&lt;/mi&gt;&lt;/math&gt;',
                ),
                (
                    '<noscript><p title="</noscript><img src=x onerror=alert(1)>">',
                    '&lt;noscript&gt;<p title="&lt;/noscript&gt;&lt;img src=x '
                    'onerror=alert(1)&gt;"></p>',
                ),
                ("<!--<script>alert(1)</script>-->", ""),
            ]
        )

    def test_table_alignment_is_kept(self):
        self.assertSanitized(
            [
                (
                    "| a | b |\n|:-:|--:|\n| 1 | 2 |",
                    "<table>\n<thead>\n<tr>\n<th>a</th>\n<th>b</th>\n</tr>\n</thead>\n"
                    '<tbody>\n<tr>\n<td align="center">1</td>\n'
                    '<td align="right">2</td>\n</tr>\n</tbody>\n</table>',
                ),
            ]
        )


if __name__ == "__main__":
    unittest.main()
    # k = TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult()
    # unittest.TextTestRunner().run(k)
