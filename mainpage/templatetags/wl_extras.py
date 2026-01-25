#!/usr/bin/env python -tt
# encoding: utf-8

from django import template
from django.conf import settings
from mainpage.wl_utils import return_git_path
import subprocess

register = template.Library()


@register.simple_tag
def current_year():
    """Just return the current year."""

    from datetime import date

    return date.today().year


@register.simple_tag
def wl_logo():
    """Just return the name of the logo."""

    return settings.LOGO_FILE


@register.filter
def get_model_name(object):
    """Returns the name of an objects model."""
    return object.__class__.__name__


@register.simple_tag
def git_data():
    """Just return the name the current git branch and commit."""

    git_path = return_git_path()
    text = ""
    if settings.SHOW_GIT_DATA and git_path:
        try:
            branch = subprocess.check_output(
                [git_path, "symbolic-ref", "--short", "HEAD"]
            )
            commit = subprocess.check_output([git_path, "rev-parse", "--short", "HEAD"])
            text = f"On branch '{branch.decode()}' with commit '{commit.decode()}'"
        except subprocess.CalledProcessError as e:
            text = e
    return text
