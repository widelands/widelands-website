#!/usr/bin/env python -tt
# encoding: utf-8
from django.urls import re_path, include

urlpatterns = [
    "",
    # 3rd party, modified for widelands
    re_path(r"^wiki/", include("wiki.urls")),
    re_path(r"^forum/", include("pybb.urls")),
    # WL specific:
    re_path(r"^$", lambda *args, **kwargs: None, name="mainpage"),
    re_path(r"^webchat/", include("wlwebchat.urls")),
    re_path(r"^maps/", include("wlmaps.urls")),
    re_path(r"^screenshots/", include("wlscreens.urls")),
    re_path(r"^wlscreens/", include("wlscreens.urls")),
]
