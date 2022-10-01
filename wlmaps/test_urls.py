#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *

urlpatterns = [
    url(r"^wlmaps/", include("wlmaps.urls")),
]
