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
from django.contrib.auth.models import User
from django.conf import settings

register = template.Library()


@register.filter
def user_link(user):

    if not hasattr(user, 'email') or user.email == settings.DELETED_MAIL_ADDRESS:
        return 'User deleted'
    else:
        data = u'<a href="%s">%s</a>' % (
            reverse('profile_view', args=[user.username]), user.username)
    return mark_safe(data)
