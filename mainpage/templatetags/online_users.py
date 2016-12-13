#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: online_user.py
#
# Created by Holger Rapp on 2009-02-19.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: 2009-02-20 22:37:16
#

from django import template
from django.contrib.auth.models import User
from django.db.models import Count
import datetime
from tracking.models import Visitor

register = template.Library()


@register.inclusion_tag('mainpage/online_users.html')
def online_users(num):
    """Show user that has been login an hour ago."""
    users = [l.user for l in Visitor.objects.active().exclude(user=None)]

    # There might still be duplicates, so we make a set and order it into
    # a list again
    users = sorted(list(set(users)), key=lambda user: user.username)

    return {
        'users': users,
    }
