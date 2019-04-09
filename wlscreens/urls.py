#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from models import Category, Screenshot
from views import *

urlpatterns = [
    url(r'^$', CategoryList.as_view(), name='wlscreens_index'),
]
