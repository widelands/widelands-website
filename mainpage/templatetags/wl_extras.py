#!/usr/bin/env python -tt
# encoding: utf-8

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def current_year():
    """Just return the current year."""

    from datetime import date

    return date.today().year


@register.simple_tag
def wl_logo():
    """Just return the name of the logo."""

    from django.conf import settings

    return settings.LOGO_FILE


@register.filter
def get_model_name(object):
    """Returns the name of an objects model."""
    return object.__class__.__name__
