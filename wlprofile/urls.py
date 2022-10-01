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

from django.conf.urls import *
from . import views

urlpatterns = [
    url(r"^edit/$", views.edit, name="profile_edit"),
    url(r"^delete/$", views.delete_me, name="delete_me"),
    url(r"^do_delete/$", views.do_delete, name="do_delete"),
    url(r"^(?P<user>.*)/$", views.view, name="profile_view"),
    url(r"^$", views.view, name="profile_view"),
]
