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
import sys; sys.path.append("..")

import unittest
from wiki.models import Article
from django.contrib.sites.models import Site
from settings import SITE_ID
from django.test import TestCase as DBTestCase
_domain = Site.objects.get(pk=SITE_ID).domain

from templatetags.wl_markdown import do_wl_markdown

class TestWlMarkdown(DBTestCase):
    def setUp(self):
        a = Article.objects.create(title="MainPage")
        a = Article.objects.create(title="HalloWelt")
        a = Article.objects.create(title="NoWikiWord")
        a = Article.objects.create(title="WikiWord")

    def _check(self, input, wanted):
        res = do_wl_markdown(input)
        self.assertEqual(wanted,res)

    def test_simple_case__correct_result(self):
        input = u"Hallo Welt"
        wanted = u"<p>Hallo Welt</p>"
        self._check(input,wanted)

    def test_wikiwords_simple__except_correct_result(self):
        input = u"Na Du HalloWelt, Du?"
        wanted = u"""<p>Na Du <a href="/wiki/HalloWelt">HalloWelt</a>, Du?</p>"""
        self._check(input,wanted)

    def test_wikiwords_avoid__except_correct_result(self):
        input = u"Hi !NotAWikiWord Moretext"
        wanted = u"""<p>Hi NotAWikiWord Moretext</p>"""
        self._check(input,wanted)

    def test_wikiwords_in_link__except_correct_result(self):
        input = u"""WikiWord [NoWikiWord](/forum/)"""
        wanted = u"""<p><a href="/wiki/WikiWord">WikiWord</a> <a href="/forum/">NoWikiWord</a></p>"""
        self._check(input,wanted)

    def test_wikiwords_external_links__except_correct_result(self):
        input = u"""[NoWikiWord](http://www.sun.com)"""
        wanted = u"""<p><a href="http://www.sun.com" class="external">NoWikiWord</a></p>"""
        self._check(input,wanted)

    def test_wikiwords_noexternal_links__except_correct_result(self):
        input = u"""[NoWikiWord](http://%s/blahfasel/wiki)""" % _domain
        wanted = u"""<p><a href="http://%s/blahfasel/wiki">NoWikiWord</a></p>""" %_domain
        self._check(input,wanted)

    def test_wikiwords_noclasschangeforimage_links__except_correct_result(self):
        input =  u"""<a href="http://www.ccc.de"><img src="/blub" /></a>"""
        wanted = u"""<p><a href="http://www.ccc.de"><img src="/blub" /></a></p>"""
        self._check(input,wanted)

    # Existing links
    def test_existing_link_html(self):
        input = u"""<a href="/wiki/MainPage">this page</a>"""
        wanted = u"""<p><a href="/wiki/MainPage">this page</a></p>"""
        self._check(input,wanted)

    def test_existing_link_markdown(self):
        input = u"""[this page](/wiki/MainPage)"""
        wanted = u"""<p><a href="/wiki/MainPage">this page</a></p>"""
        self._check(input,wanted)

    def test_existing_link_wikiword(self):
        input = u"""MainPage"""
        wanted = u"""<p><a href="/wiki/MainPage">MainPage</a></p>"""
        self._check(input,wanted)

    def test_existing_editlink_wikiword(self):
        input = u"""<a href="/wiki/MainPage/edit/">this page</a>"""
        wanted = u"""<p><a href="/wiki/MainPage/edit/">this page</a></p>"""
        self._check(input,wanted)

    # Missing links
    def test_missing_link_html(self):
        input = u"""<a href="/wiki/MissingPage">this page</a>"""
        wanted = u"""<p><a href="/wiki/MissingPage" class="missing">this page</a></p>"""
        self._check(input,wanted)

    def test_missing_link_markdown(self):
        input = u"""[this page](/wiki/MissingPage)"""
        wanted = u"""<p><a href="/wiki/MissingPage" class="missing">this page</a></p>"""
        self._check(input,wanted)

    def test_missing_link_wikiword(self):
        input = u"""BlubMissingPage"""
        wanted = u"""<p><a href="/wiki/BlubMissingPage" class="missing">BlubMissingPage</a></p>"""
        res = do_wl_markdown(input)
        # self._check(input,wanted)

    def test_missing_editlink_wikiword(self):
        input = u"""<a href="/wiki/MissingPage/edit/">this page</a>"""
        wanted = u"""<p><a href="/wiki/MissingPage/edit/" class="missing">this page</a></p>"""
        self._check(input,wanted)

    # Check smileys
    def test_smiley_angel(self):
        input = """O:-)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-angel.png" alt="face-angel.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_crying(self):
        input = """:'-("""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-crying.png" alt="face-crying.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_devilish(self):
        input = """>:-)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-devilish.png" alt="face-devilish.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_glasses(self):
        input = """8-)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-glasses.png" alt="face-glasses.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_kiss(self):
        input = """:-x"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-kiss.png" alt="face-kiss.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_plain(self):
        input = """:-|"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-plain.png" alt="face-plain.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_sad(self):
        input = """:-("""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-sad.png" alt="face-sad.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_smilebig(self):
        input = """:))"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-smile-big.png" alt="face-smile-big.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_smile(self):
        input = """:-)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-smile.png" alt="face-smile.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_surprise(self):
        input = """:-O"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-surprise.png" alt="face-surprise.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_wink(self):
        input = """;-)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-wink.png" alt="face-wink.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_grin(self):
        input = """:D"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-grin.png" alt="face-grin.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_sad(self):
        input = """:("""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-sad.png" alt="face-sad.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_smile(self):
        input = """:)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-smile.png" alt="face-smile.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_surprise(self):
        input = """:O"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-surprise.png" alt="face-surprise.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_wink(self):
        input = """;)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-wink.png" alt="face-wink.png" /></p>"""
        self._check(input,wanted)
    def test_smiley_monkey(self):
        input = """:(|)"""
        wanted = u"""<p><img src="/wlmedia/img/smileys/face-monkey.png" alt="face-monkey.png" /></p>"""
        self._check(input,wanted)


    # Occured errors
    def test_wiki_rootlink(self):
        input = u"""<a href="/wiki">this page</a>"""
        wanted = u"""<p><a href="/wiki">this page</a></p>"""
        self._check(input,wanted)
    def test_wiki_rootlink_with_slash(self):
        input = u"""<a href="/wiki/">this page</a>"""
        wanted = u"""<p><a href="/wiki/">this page</a></p>"""
        self._check(input,wanted)

    # Special pages
    def test_wiki_specialpage(self):
        input = u"""<a href="/wiki/list">this page</a>"""
        wanted = u"""<p><a href="/wiki/list">this page</a></p>"""
        self._check(input,wanted)
    def test_wiki_specialpage_markdown(self):
        input = u"""[list](/wiki/list)"""
        wanted = u"""<p><a href="/wiki/list">list</a></p>"""
        self._check(input,wanted)

    # Special problem with emphasis
    def test_markdown_emphasis_problem(self):
        input = u"""*This is bold*  _This too_\n\n"""
        wanted = u"""<p><em>This is bold</em> <em>This too</em></p>"""
        self._check(input,wanted)

    # Another markdown problem with alt tag escaping
    def test_markdown_alt_problem(self):
        # {{{ Test strings
        input = u"""![img_thisisNOTitalicplease_name.png](/wlmedia/blah.png)\n\n"""
        wanted = u'<p><img alt="img_thisisNOTitalicplease_name.png" src="/wlmedia/blah.png" /></p>'
        # }}}
        self._check(input,wanted)

    def test_emptystring_problem(self):
        # {{{ Test strings
        input = u''
        wanted = u''
        # }}}
        self._check(input,wanted)

    # Damned problem with tables
    def test_markdown_table_problem(self):
        # {{{ Test strings
        input = u"""
Header1 | Header 2
------- | --------
Value 1 | Value 2
Value 3 | Value 4
"""
        wanted = u"""<table>
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
        self._check(input,wanted)
    def test_svnrevision_replacement( self ):
        input = u"- Fixed this bug (bzr:r3222)"
        wanted = u"""<ul>\n<li>Fixed this bug (<a href="http://bazaar.launchpad.net/%7Ewidelands-dev/widelands/trunk/revision/3222" class="external">r3222</a>)</li>\n</ul>"""
        self._check(input,wanted)
    def test_svnrevision_multiple_replacement( self ):
        input = u"- Fixed this bug (bzr:r3222, bzr:r3424)"
        wanted = u"""<ul>\n<li>Fixed this bug (<a href="http://bazaar.launchpad.net/%7Ewidelands-dev/widelands/trunk/revision/3222" class="external">r3222</a>, <a href="http://bazaar.launchpad.net/%7Ewidelands-dev/widelands/trunk/revision/3424" class="external">r3424</a>)</li>\n</ul>"""
        self._check(input,wanted)


if __name__ == '__main__':
    unittest.main()
    # k = TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult()
    # unittest.TextTestRunner().run(k)

