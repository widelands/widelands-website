#! /usr/bin/env python


'''
SemanticWikiLinks Extension for Python-Markdown
===============================================

Adds support for semantic (wiki)links (RDFa).

Converts links of style `[[rel :: target | label ]]`, where `rel` and `label`
are optional.

Customizable with `make_link` option as to what the actual element is.


Usage
-----

    >>> text = "Some text with a [[WikiLink]]."
    >>> html = markdown.markdown(text, ['semanticwikilinks'])
    >>> print(html)
    <p>Some text with a <a href="WikiLink">WikiLink</a>.</p>

    >>> text = "[[http://activearchives.org/]], [[#id|anchor]], [[../index.html|a relative link]], [[/|an absolute link]], [[/index.html|another absolute link]]"
    >>> html = markdown.markdown(text, ['semanticwikilinks'])
    >>> print(html)
    <p><a href="http://activearchives.org/">http://activearchives.org/</a>, <a href="#id">anchor</a>, <a href="../index.html">a relative link</a>, <a href="/">an absolute link</a>, <a href="/index.html">another absolute link</a></p>

Define a custom URL builder:

    >>> from markdown.util import etree
    >>> def make_rdfa(md, rel, target, label):
    ...     # `md` is the Markdown instance
    ...     elt = etree.Element("span")
    ...     elt.set("property", rel)
    ...     elt.set("value", target)
    ...     elt.text = label or target
    ...     return elt

    >>> md = markdown.Markdown(extensions=['semanticwikilinks'],
    ...         extension_configs={'semanticwikilinks' : [('make_link', make_rdfa)]})
    >>> html = md.convert('[[ Speaker :: Sherry Turkle | Second Self ]]')
    >>> print(html)
    <p><span property="aa:Speaker" value="Sherry Turkle">Second Self</span></p>

Change the default namespace (which is "aa"):

    >>> md = markdown.Markdown(extensions=['semanticwikilinks'],
    ...         extension_configs={'semanticwikilinks' : [('namespace', 'mynamespace')]})
    >>> html = md.convert('[[ Speaker :: Sherry Turkle | Second Self ]]')
    >>> print(html)
    <p><a href="Sherry Turkle" rel="mynamespace:Speaker">Second Self</a></p>

To do
-----

- An optional function to wikify names? (It is already possible to achieve
this with the custom `make_link` function).


Dependencies
------------

* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)


Copyright
---------

2011, 2012 [The active archives contributors](http://activearchives.org/)
2011, 2012 [Michael Murtaugh](http://automatist.org/)
2011, 2012 [Alexandre Leray](http://stdin.fr/)

All rights reserved.

This software is released under the modified BSD License. 
See LICENSE.md for details.
'''


import markdown
try:
    from markdown import etree
except ImportError:
    from markdown.util import etree
import re


__version__ = '1.1.1'


WIKILINK_RE = r"""
\[\[\s*
    (?:((?P<namespace>\w+):)?(?P<rel>[^\]#]+?) \s* ::)? \s*
    (?P<target>.+?) \s*
    (?:\| \s* (?P<label>.+?) \s*)?
\]\](?!\])
""".strip()


def make_link(md, rel, target, label):
    a = etree.Element('a')
    a.set('href', target)
    if rel:
        a.set('rel', rel)
    a.text = label or target
    return a


def make_wikilink(md, rel, target, label):
    # Turns a link from Syntax [[ Page Name | linktext ]]
    a = etree.Element('a')
    a.set('href', '/wiki/' + target)
    a.set('class', 'wikilink')
    if rel:
        pass
    a.text = label or target
    return a


class SemanticWikiLinkExtension(markdown.Extension):

    def __init__(self, *args, **kwargs):
        self.config = {
            'make_link': [make_wikilink, 'Callback to convert link parts into an HTML/etree element'],
            'namespace': ['aa', 'Default namespace'],
        }
        super(SemanticWikiLinkExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        # append to end of inline patterns
        ext = SemanticWikiLinkPattern(self.config, md)
        md.inlinePatterns.add('semanticwikilink', ext, '<not_strong')


class SemanticWikiLinkPattern(markdown.inlinepatterns.Pattern):

    def __init__(self, config, md=None):
        markdown.inlinepatterns.Pattern.__init__(self, '', md)
        self.compiled_re = re.compile(
            '^(.*?)%s(.*?)$' % WIKILINK_RE, re.DOTALL | re.X)
        self.config = config

    def getCompiledRegExp(self):
        return self.compiled_re

    def handleMatch(self, m):
        """Returns etree."""
        d = m.groupdict()
        fn = self.config['make_link'][0]
        namespace = d.get('namespace') or self.config['namespace'][0]
        rel = d.get('rel')

        if rel:
            rel = '%s:%s' % (namespace, d.get('rel'))

        return fn(self.markdown, rel, d.get('target'), d.get('label'))


def makeExtension(*args, **kwargs):
    return SemanticWikiLinkExtension(*args, **kwargs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
