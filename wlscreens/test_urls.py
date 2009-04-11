#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^wlscreens/', include("wlscreens.urls")),
)

