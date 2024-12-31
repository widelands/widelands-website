#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlggz/admin.py
#
# Created 2010-06-03 by Timo Wingender <timo.wingender@gmx.de>
#
# Last Modified: $Date$
#

from django.contrib import admin
from .models import GGZAuth


class GGZAdmin(admin.ModelAdmin):
    list_display = ["user", "password", "permissions"]
    list_per_page = 20
    ordering = ["-user"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    fieldsets = ((None, {"fields": ("user", "password", "permissions")}),)


admin.site.register(GGZAuth, GGZAdmin)
