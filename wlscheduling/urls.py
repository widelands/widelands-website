#!/usr/bin/env python -tt
# encoding: utf-8
from django.urls import re_path
from .views import scheduling, scheduling_main, scheduling_find

urlpatterns = [
    re_path(r"^scheduling/$", scheduling, name="scheduling_scheduling"),
    re_path(r"^main/$", scheduling_main, name="scheduling_main"),
    re_path(r"^find/$", scheduling_find, name="scheduling_find"),
]
