#!/usr/bin/env python -tt
# encoding: utf-8

from django import template
from datetime import date

register = template.Library()

@register.simple_tag
def current_year():
    """Just return the current year."""
    return date.today().year
