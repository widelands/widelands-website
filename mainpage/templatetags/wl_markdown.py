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

register = template.Library()

link_patterns = [
    # Match a wiki page link LikeThis.
    (re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)"), r"/wiki/\1")
]

def do_wl_markdown( value, *args, **keyw ):
    return markdown2.markdown(value, extras = [ "footnotes", "link-patterns"], link_patterns=link_patterns, *args, **keyw)

@register.filter
def wl_markdown(value, arg=''):
    """
    My own markup filter, wrapping the markup2 library, which is less bugged.
    """
    return mark_safe(force_unicode(do_wl_markdown(smart_str(value))))
wl_markdown.is_safe = True

