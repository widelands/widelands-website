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
import datetime

register = template.Library()

@register.inclusion_tag('mainpage/online_users.html')
def online_users(num):
    """
    Show user that has been login an hour ago.
    """
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    sql_datetime = datetime.datetime.strftime(one_hour_ago, '%Y-%m-%d %H:%M:%S')
    users = User.objects.filter(last_login__gt=sql_datetime,
                                is_active__exact=1).order_by('-last_login')[:num]
    return {
            'users': users,
    }

