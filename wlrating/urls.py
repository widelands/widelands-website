#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from .view import rating_main, arbiter

urlpatterns = [
    url(r'^main/$', rating_main, name='rating_main'),
    url(r'^arbiter/$', arbiter, name='arbiter'),
]
