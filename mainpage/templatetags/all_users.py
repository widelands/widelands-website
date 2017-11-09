#!/usr/bin/env python -tt
# encoding: utf-8

from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag
def all_users():
    """Provide a list of all users"""
    return [str(u.username) for u in User.objects.all()]
