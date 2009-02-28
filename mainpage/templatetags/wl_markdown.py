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

register = template.Library()

custom_filters = [
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
            rv = pattern.sub( replacement, text )
            if rv:
                text.replaceWith(rv)
                # Only one replacement allowed!
                break
    return unicode(soup)


@register.filter
def wl_markdown(value, arg=''):
    """
    My own markup filter, wrapping the markup2 library, which is less bugged.
    """
    return mark_safe(force_unicode(do_wl_markdown(smart_str(value))))
wl_markdown.is_safe = True

