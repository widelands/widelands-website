#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from models import Category, Screenshot
from views import *

urlpatterns = patterns('',
    url(r'^$', index, name="wlscreens_index" ),
    url(r'^(?P<category_slug>[-\w]+)/$', category, name = "wlscreens_category" ),
)

