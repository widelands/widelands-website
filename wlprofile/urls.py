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

from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
   url(r'^edit/$', views.edit, name='profile_edit'),
   url(r'^(?P<user>.*)/$', views.view, name='profile_view'),
   url(r'^$', views.view, name='profile_view'),
)

