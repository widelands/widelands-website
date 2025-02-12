#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlprofile/urls.py
#
# Created by Holger Rapp on 2009-03-15.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^edit/$", views.edit, name="profile_edit"),
    re_path(r"^subscriptions/$", views.show_subscriptions, name="subscriptions"),
    re_path(r"^unsubscribe_topics/$", views.unsubscribe_topics, name="unsubscribe_topics"),
    re_path(r"^unsubscribe_other/$", views.unsubscribe_other, name="unsubscribe_other"),
    re_path(r"^delete/$", views.delete_me, name="delete_me"),
    re_path(r"^do_delete/$", views.do_delete, name="do_delete"),
    re_path(r"^(?P<user>.*)/$", views.view, name="profile_view"),
    re_path(r"^$", views.view, name="profile_view"),
]
