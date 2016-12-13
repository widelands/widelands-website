#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: mainpage/templatetags/wl_markdown.py
#
# Created by Holger Rapp on 2009-02-27.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from settings import BLEACH_ALLOWED_TAGS, BLEACH_ALLOWED_ATTRIBUTES

# Try to get a not so fully broken markdown module
import markdown
if markdown.version_info[0] < 2:
    raise ImportError, 'Markdown library to old!'
from markdown import markdown
import re
import bleach

from BeautifulSoup import BeautifulSoup, NavigableString

# If we can import a Wiki module with Articles, we
# will check for internal wikipages links in all internal
# links starting with /wiki/
try:
    from wiki.models import Article, ChangeSet
    check_for_missing_wikipages = True
except ImportError:
    check_for_missing_wikipages = False

# We will also need the site domain
from django.contrib.sites.models import Site
from settings import SITE_ID, SMILEYS, SMILEY_DIR, \
    SMILEY_PREESCAPING, BZR_URL

try:
    _domain = Site.objects.get(pk=SITE_ID).domain
except:
    _domain = ''

# Getting local domain lists
try:
    from settings import LOCAL_DOMAINS as _LOCAL_DOMAINS
    LOCAL_DOMAINS = [_domain] + _LOCAL_DOMAINS
except ImportError:
    LOCAL_DOMAINS = [_domain]


register = template.Library()


def _insert_smileys(text):
    """This searches for smiley symbols in the current text and replaces them
    with the correct images.

    Only replacing if smiley symbols aren't in a word (e.g. http://....)

    """
    words = text.split(' ')
    for sc, img in SMILEYS:
        if sc in words:
            words[words.index(
                sc)] = "<img src='%s%s' alt='%s' />" % (SMILEY_DIR, img, img)
    text = ' '.join(words)
    return text


def _insert_smiley_preescaping(text):
    """This searches for smiley symbols in the current text and replaces them
    with the correct images."""
    for before, after in SMILEY_PREESCAPING:
        text = text.replace(before, after)
    return text


revisions_re = [
    re.compile('bzr:r(\d+)'),
]


def _insert_revision(text):
    for r in revisions_re:
        text = r.sub( lambda m: """<a href="%s">r%s</a>""" % (
            settings.BZR_URL % m.group(1), m.group(1)), text)
    return text


def _classify_link(tag):
    """Returns a classname to insert if this link is in any way special
    (external or missing wikipages)

    tag to classify for

    """
    # No class change for image links
    if tag.findChild('img') != None:
        return None

    href = tag['href'].lower()

    # Check for external link
    if href.startswith('http'):
        for domain in LOCAL_DOMAINS:
            external = True
            if href.find(domain) != -1:
                external = False
                break
        if external:
            return {'class': 'externalLink', 'title': 'This link refers to outer space'}

    if '/profile/' in (tag['href']):
        return {'class': 'userLink', 'title': 'This link refers to a userpage'}

    if check_for_missing_wikipages and href.startswith('/wiki/'):

        # Check for missing wikilink /wiki/PageName[/additionl/stuff]
        # Using href because we need cAsEs here
        pn = tag['href'][6:].split('/', 1)[0]

        if not len(pn):  # Wiki root link is not a page
            return {'class': 'wrongLink', 'title': 'This Link misses an articlename'}

        # Wiki special pages are also not counted
        if pn in ['list', 'search', 'history', 'feeds', 'observe', 'edit']:
            return {'class': 'specialLink'}

        # Check for a redirect
        try:
            # try to get the article id; if this fails an IndexError is raised
            a_id = ChangeSet.objects.filter(
                old_title=pn).values_list('article_id')[0]

            # get actual title of article
            act_t = Article.objects.get(id=a_id[0]).title
            if pn != act_t:
                return {'title': "This is a redirect and points to \"" + act_t + "\""}
            else:
                return None
        except IndexError:
            pass

        # article missing (or misspelled)
        if Article.objects.filter(title=pn).count() == 0:
            return {'class': 'missingLink', 'title': 'This Link is misspelled or missing. Click to create it anyway.'}

    return None


def _clickable_image(tag):
    # is external link?
    if tag['src'].startswith('http'):
        # is allways a link?
        if tag.parent.name != 'a':
            # add link to image
            text = '<a href=' + tag['src'] + \
                '><img src=' + tag['src'] + '></a>'
            return text
    return None


custom_filters = {
    # Wikiwordification
    # Match a wiki page link LikeThis. All !WikiWords (with a !
    # in front) are ignored
    'wikiwords': (re.compile(r"(!?)(\b[A-Z][a-z]+[A-Z]\w+\b)"), lambda m:
                  m.group(2) if m.group(1) == '!' else
                  u"""<a href="/wiki/%(match)s">%(match)s</a>""" %
                  {'match': m.group(2)}),

}


def do_wl_markdown(value, *args, **keyw):
    # Do Preescaping for markdown, so that some things stay intact
    # This is currently only needed for this smiley ">:-)"
    value = _insert_smiley_preescaping(value)
    custom = keyw.pop('custom', True)
    html = smart_str(markdown(value, extensions=[
                     'extra', 'toc'], *args, **keyw))

    # Sanitize posts from potencial untrusted users (Forum/Wiki/Maps)
    if 'bleachit' in args:
        html = mark_safe(bleach.clean(
            html, tags=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRIBUTES))

    # Since we only want to do replacements outside of tags (in general) and not between
    # <a> and </a> we partition our site accordingly
    # BeautifoulSoup does all the heavy lifting
    soup = BeautifulSoup(html)
    if len(soup.contents) == 0:
        # well, empty soup. Return it
        return unicode(soup)

    for text in soup.findAll(text=True):
        # Do not replace inside a link
        if text.parent.name == 'a':
            continue

        # We do our own small preprocessing of the stuff we got, after markdown
        # went over it General consensus is to avoid replacing anything in
        # links [blah](blkf)
        if custom:
            # Replace bzr revisions
            rv = _insert_revision(text)
            # Replace smileys; only outside "code-tags"
            if not text.parent.name == 'code':
                rv = _insert_smileys(rv)

            for name, (pattern, replacement) in custom_filters.iteritems():
                if not len(text.strip()) or not keyw.get(name, True):
                    continue

                rv = pattern.sub(replacement, rv)
            text.replaceWith(rv)

    # This call slows the whole function down...
    # unicode->reparsing.
    # The function goes from .5 ms to 1.5ms on my system
    # Well, for our site with it's little traffic it's maybe not so important...
    # What a waste of cycles :(
    soup = BeautifulSoup(unicode(soup))
    # We have to go over this to classify links
    for tag in soup.findAll('a'):
        rv = _classify_link(tag)
        if rv:
            for attribute in rv.iterkeys():
                tag[attribute] = rv.get(attribute)

    # All external images gets clickable
    # This applies only in forum
    for tag in soup.findAll('img'):
        link = _clickable_image(tag)
        if link:
            tag.replaceWith(link)

    return unicode(soup)


@register.filter
def wl_markdown(content, arg=''):
    """A Filter which decides when to 'bleach' the content."""
    if arg == 'bleachit':
        return mark_safe(do_wl_markdown(content, 'bleachit'))
    else:
        return mark_safe(do_wl_markdown(content))
