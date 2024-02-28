#!/usr/bin/env python -tt
# encoding: utf-8
from django.urls import *
from .models import Category, Screenshot
from .views import *

urlpatterns = [
    re_path(r"^$", CategoryList.as_view(), name="wlscreens_index"),
]
