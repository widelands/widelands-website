#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from views import scheduling, scheduling_main, scheduling_find

urlpatterns = [
    url(r'^scheduling/$', scheduling, name='scheduling_scheduling'),
    url(r'^main/$', scheduling_main, name='scheduling_main'),
    url(r'^find/$', scheduling_find, name='scheduling_find'),
]
