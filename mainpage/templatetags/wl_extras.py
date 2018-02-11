#!/usr/bin/env python -tt
# encoding: utf-8

from django import template

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


@register.simple_tag
def all_users():
    """Provide a list of all users."""
    from django.contrib.auth.models import User
    return [str(u.username) for u in User.objects.all()]


@register.inclusion_tag('mainpage/forum_navigation.html')
def forum_navigation():
    from pybb.models import Category
    """Makes the forum list available to the navigation, even
    if it is not loaded directly.

    Ordering:
    1.: value of 'Position' in pybb.Category
    2.: value of 'Position' of pybb.Forum.

    """
    categories = Category.objects.all()
    return {'categories': categories}


@register.filter
def get_model_name(object):
    """Returns the name of an objects model."""
    return object.__class__.__name__
