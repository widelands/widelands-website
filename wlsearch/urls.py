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
import views

urlpatterns = patterns('',
   url(r'^$', views.search, name='search'),
)

