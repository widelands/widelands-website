#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Get acces to additional models which are not set by Django by default.

So Djangos orm is used when changing things, e.g. delete a permission.

"""

from django.contrib import admin
from django.contrib.auth.models import Permission
admin.site.register(Permission)
