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

register = template.Library()

@register.filter
def wl_markdown(value, arg=''):
    """
    My own markup filter, wrapping the markup2 library, which is less bugged.
    """
    return mark_safe(force_unicode(markdown2.markdown(smart_str(value))))
wl_markdown.is_safe = True

