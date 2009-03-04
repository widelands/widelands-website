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
import markdown2
import re

from BeautifulSoup import BeautifulSoup

# If we can import a Wiki module with Articles, we
# will check for internal wikipages links in all internal 
# links starting with /wiki/
try:
    from widelands.wiki.models import Article
    check_for_missing_wikipages = True
except ImportError:
    check_for_missing_wikipages = False

# We will also need the site domain
from django.contrib.sites.models import Site
from settings import SITE_ID
_domain = Site.objects.get(pk=SITE_ID).domain

# Getting local domain lists
try:
    from settings import LOCAL_DOMAINS as _LOCAL_DOMAINS
    LOCAL_DOMAINS = [ _domain ] + _LOCAL_DOMAINS
except ImportError:
    LOCAL_DOMAINS = [ _domain ] 


register = template.Library()

def _classify_link( tag ):
    """
    Returns a classname to insert if this link is in any way
    special (external or missing wikipages)

    tag to classify for
    """
    # No class change for image links
    if tag.findChild("img") != None:
        return None
    
    href = tag["href"].lower()
    
    # Check for external link
    if href.startswith("http"):
        for domain in LOCAL_DOMAINS:
            external = True
            if href.find(domain) != -1:
                external = False
                break
        if external:
            return "external"
    
    if check_for_missing_wikipages and href.startswith("/wiki"):
        # Check for missing wikilink /wiki/PageName[/additionl/stuff]
        # Using href because we need cAsEs here
        pn = tag["href"][6:].split('/',1)[0]
        
        if not len(pn): # Wiki root link is not a page
            return None

        # Wiki special pages are also not counted
        if pn in ["list","search","history","feeds","observe","edit" ]:
            return None

        if Article.objects.filter(title=pn).count() == 0:
            return "missing"

    return None 

custom_filters = [
    # Wikiwordification
    # Match a wiki page link LikeThis. All !WikiWords (with a ! in front) are ignored
    (re.compile(r"(!?)(\b[A-Z][a-z]+[A-Z]\w+\b)"), lambda m: m.group(2) if m.group(1) == '!' \
        else u"""<a href="/wiki/%(match)s">%(match)s</a>""" % {"match": m.group(2) }),
    
]

def do_wl_markdown( value, *args, **keyw ):
    nvalue = markdown2.markdown(value, extras = [ "footnotes"], *args, **keyw)
    
    # Since we only want to do replacements outside of tags (in general) and not between
    # <a> and </a> we partition our site accordingly
    # BeautifoulSoup does all the heavy lifting
    soup = BeautifulSoup(nvalue)
    ctag = soup.contents[0]

    for text in soup.findAll(text=True):
        # Do not replace inside a link
        if text.parent.name == "a":
            continue

        # We do our own small preprocessing of the stuff we got, after markdown went over it
        # General consensus is to avoid replacing anything in links [blah](blkf)
        for pattern,replacement in custom_filters:
            if not len(text.strip()):
                continue

            rv = pattern.sub( replacement, text )
            if rv:
                # We can't do a simple text substitution, because we 
                # need this parsed for further processing
                # Hmpf, this code didn't work, so we DID text substitution
                # and then reparsedj
                # ns = BeautifulSoup(rv)
                # text.replaceWith(BeautifulSoup(rv))
                text.replaceWith(rv)
                # Only one replacement allowed!
                break
    
    # This call slows the whole function down... 
    # unicode->reparsing. 
    # The function goes from .5 ms to 1.5ms on my system
    # Well, for our site with it's little traffic it's maybe not so important... 
    soup = BeautifulSoup(unicode(soup)) # What a waste of cycles :(

    # We have to go over this to classify links
    for tag in soup.findAll("a"):
        rv = _classify_link(tag)
        if rv:
            tag["class"] = rv

    return unicode(soup)


@register.filter
def wl_markdown(value, arg=''):
    """
    My own markup filter, wrapping the markup2 library, which is less bugged.
    """
    return mark_safe(force_unicode(do_wl_markdown(smart_str(value))))
wl_markdown.is_safe = True

