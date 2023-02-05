#!/usr/bin/env python -tt
# encoding: utf-8
from django.urls import *

urlpatterns = [
    re_path(r"^wlmaps/", include("wlmaps.urls")),
]
