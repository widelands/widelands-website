#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # 3rd party, modified for widelands
    (r'^wiki/', include('wiki.urls')),
    (r'^forum/', include('pybb.urls')),

    # WL specific:
    url(r'^$', lambda *args, **kwargs: None, name="mainpage"),
    url(r'^webchat/', include("wlwebchat.urls")),
    url(r'^maps/', include("wlmaps.urls")),
    url(r'^screenshots/', include("wlscreens.urls")),
    url(r'^wlscreens/', include("wlscreens.urls")),
)

