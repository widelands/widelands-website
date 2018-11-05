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
from markdownextensions.semanticwikilinks.mdx_semanticwikilinks import SemanticWikiLinkExtension

# Try to get a not so fully broken markdown module
import markdown
if markdown.version_info[0] < 2:
    raise ImportError, 'Markdown library to old!'
from markdown import markdown
import re
import urllib
import bleach

from bs4 import BeautifulSoup, NavigableString

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
    SMILEY_PREESCAPING

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
    
    Then we have to reassemble the whole contents..."""
    
    tmp_content = []
    for content in text.parent.contents:
        try:
            # if this fails, content is probably a tag, eg: <br />
            words = content.split(' ')
        except:
            # apply the unsplittable content and continue
            tmp_content.append(content)
            continue
        
        for i, word in enumerate(words):
            smiley = ""
            for sc, img in SMILEYS:
                if word == sc:
                    smiley = img
            if smiley:
                tmp_content.append(BeautifulSoup(features="lxml").new_tag('img', src="{}{}".format(SMILEY_DIR, smiley)))
            else:
                if i < (len(words) - 1):
                    # Apply a space after each word, except the last word
                    word = word + ' '
                tmp_content.append(NavigableString(word))
    # Changing the main bs4-soup directly here -> no return value
    text.parent.contents = [x for x in tmp_content]



def _insert_smiley_preescaping(text):
    """This searches for smiley symbols in the current text and replaces them
    with the correct images."""
    for before, after in SMILEY_PREESCAPING:
        text = text.replace(before, after)
    return text


def _classify_link(tag):
    """Returns a classname to insert if this link is in any way special
    (external or missing wikipages)

    tag to classify for

    """
    # No class change for image links
    if tag.findChild('img') != None:
        return None

    try:
        href = tag['href'].lower()
    except KeyError:
        return None

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
        pn = urllib.unquote(tag['href'][6:].split('/', 1)[0])

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
        # is allready a link?
        if tag.parent.name != 'a':
            # add link to image
            new_link = BeautifulSoup(features="lxml").new_tag('a')
            new_link['href'] = tag['src']
            new_img = BeautifulSoup(features="lxml").new_tag('img')
            new_img['src'] = tag['src']
            new_img['alt'] = tag['alt']
            new_link.append(new_img)
            return new_link
    return None

FORBIDDEN_TAGS = ['code', 'pre',]
def find_smileyable_strings(bs4_string):
    ''' Find strings that contain a smiley symbol'''

    if bs4_string.parent.name.lower() in FORBIDDEN_TAGS:
        return False

    # A BS4 Tag consists of a list called contents if the tag contains another tag:
    # E.G.the contents of the p-tag: <p>Foo<br />bar</p> is
    # ['Foo', <br />, 'bar']
    for element in bs4_string.parent.contents:
        for sc, img in SMILEYS:
            if sc in bs4_string:
                return True
    return False

# Predefine the markdown extensions here to have a clean code in
# do_wl_markdown()
md_extensions = ['extra', 'toc', SemanticWikiLinkExtension()]

def do_wl_markdown(value, *args, **keyw):
    # Do Preescaping for markdown, so that some things stay intact
    # This is currently only needed for this smiley ">:-)"

    value = _insert_smiley_preescaping(value)
    custom = keyw.pop('custom', True)
    html = smart_str(markdown(value, extensions=md_extensions))

    # Sanitize posts from potencial untrusted users (Forum/Wiki/Maps)
    if 'bleachit' in args:
        html = mark_safe(bleach.clean(
            html, tags=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRIBUTES))

    # Prepare the html and apply smileys and classes
    # BeautifulSoup objects are all references, so changing an assigned variable will
    # have directly effect on the html!
    soup = BeautifulSoup(html, features="lxml")
    if len(soup.contents) == 0:
        # well, empty soup. Return it
        return unicode(soup)

    # Insert smileys
    smiley_text = soup.find_all(string=find_smileyable_strings)
    for text in smiley_text:
        _insert_smileys(text)
        
    # Classify links
    for tag in soup.find_all('a'):
        rv = _classify_link(tag)
        if rv:
            for attribute in rv.iterkeys():
                tag[attribute] = rv.get(attribute)

    # All external images gets clickable
    # This applies only in forum
    for tag in soup.find_all('img'):
        link = _clickable_image(tag)
        if link:
            tag.replace_with(link)

    return unicode(soup)


@register.filter
def wl_markdown(content, arg=''):
    """A Filter which decides when to 'bleach' the content."""
    if arg == 'bleachit':
        return mark_safe(do_wl_markdown(content, 'bleachit'))
    else:
        return mark_safe(do_wl_markdown(content))
