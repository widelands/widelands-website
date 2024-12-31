#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlprofile/templatetags/wlprofile.py
#
# Created by Holger Rapp on 2009-03-15.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

register = template.Library()


@register.filter
def user_link(user):
    if user.is_authenticated and user.wlprofile.deleted:
        # Check for is_authenticated is needed for threadedcomments reply_to.js
        return mark_safe(
            '<span title="This user has left our community">{}</span>'.format(
                settings.DELETED_USERNAME
            )
        )
    else:
        data = '<a href="%s">%s</a>' % (
            reverse("profile_view", args=[user.username]),
            user.username,
        )
    return mark_safe(data)


@register.filter
def user_status(user):
    """Check if user has deleted himself.

    When using the search, the user is just a string, so we need to get
    the userobject.
    """

    if not isinstance(user, User):
        user_obj = get_object_or_404(User, username=user)
    else:
        user_obj = user

    if user_obj.wlprofile.deleted:
        return settings.DELETED_USERNAME

    return user
