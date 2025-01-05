#!/usr/bin/env python -tt
# encoding: utf-8
from django.urls import re_path
from .views import CategoryList

urlpatterns = [
    re_path(r"^$", CategoryList.as_view(), name="wlscreens_index"),
]
