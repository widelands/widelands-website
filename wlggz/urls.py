#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlggz/urls.py
#
# Created by Timo Wingender on 2010-06-02.
# Copyright (c) 2010 timo.wingender@gmx.de. All rights reserved.
#
# Last Modified: $Date$
#

from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
   url(r'^$', views.view, name='wlggz_main'),
   url(r'^stats/?$', views.view, name='wlggz_userstats'),
   url(r'^info/?$', views.view, name='wlggz_userinfo'),
   url(r'^stats/(?P<user>.*)', views.view, name='wlggz_userstats'),
   url(r'^info/(?P<user>.*)', views.view, name='wlggz_userinfo'),
   url(r'^changepw$', views.change_password, name='wlggz_changepw'),
   url(r'^ranking$', views.view_ranking, name='wlggz_ranking'),
)

