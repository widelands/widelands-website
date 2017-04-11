SemanticWikiLinks Extension for Python-Markdown
===============================================

Adds support for semantic (wiki)links (RDFa).

Converts links of style `[[rel :: target | label ]]`, where `rel` and `label`
are optional.

Customizable with `make_link` option as to what the actual element is.


Installation
------------

    pip install git+git://github.com/aleray/mdx_semanticwikilinks.git


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

- 2011, 2012 [The active archives contributors](http://activearchives.org/)
- 2011, 2012 [Michael Murtaugh](http://automatist.org/)
- 2011, 2012 [Alexandre Leray](http://stdin.fr/)

All rights reserved.

This software is released under the modified BSD License. 
See LICENSE.md for details.
