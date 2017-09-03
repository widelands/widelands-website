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
from views import HaystackSearchView
from haystack.query import EmptySearchQuerySet
from haystack.views import basic_search

urlpatterns = [
    #url(r'^/?$', basic_search(), name='search'),
    url(r'^/?$', HaystackSearchView.as_view(), name='search'),
    #url(r'^$', SearchView(), name='haystack_search'),
    #url(r'^$', include('haystack.urls')),
]
