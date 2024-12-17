#!/usr/bin/env python -tt
# encoding: utf-8
from django.urls import re_path
from .views import MapList, upload, view, edit_comment, download


urlpatterns = [
    re_path(r"^$", MapList.as_view(), name="wlmaps_index"),
    re_path(r"^upload/$", upload, name="wlmaps_upload"),
    re_path(r"^(?P<map_slug>[-\w]+)/$", view, name="wlmaps_view"),
    re_path(
        r"^(?P<map_slug>[-\w]+)/edit_comment/$",
        edit_comment,
        name="wlmaps_edit_comment",
    ),
    re_path(r"^(?P<map_slug>[-\w]+)/download/$", download, name="wlmaps_download"),
]
