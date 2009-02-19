#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: mainpage/templatetags/block.py
#
# Created by Holger Rapp on 2009-02-19.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def wlblock(title):
    return render_to_string('mainpage/wlblock.html', {'title': title } )

@register.simple_tag
def endwlblock():
    return render_to_string('mainpage/endwlblock.html', {} )
