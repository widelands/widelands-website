#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlggz/urls.py
#
# Created by Timo Wingender on 2010-06-02.
# Copyright (c) 2010 timo.wingender@gmx.de. All rights reserved.
#
# Last Modified: $Date$
#

from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^changepw$", views.change_password, name="wlggz_changepw"),
]
