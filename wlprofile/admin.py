#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlprofile/admin.py
#
# Created by Holger Rapp on 2009-03-15.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "time_zone", "deleted"]
    list_per_page = 20
    ordering = ["-user"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    fieldsets = (
        (None, {"fields": ("user", "time_zone", "signature", "show_signatures")}),
        (
            _("Fields displayed in forum"),
            {
                "classes": ("wide",),
                "fields": ("operating_system", "widelands_version", "location"),
            },
        ),
        (
            _("Other fields"),
            {
                "classes": ("collapse",),
                "fields": ("webservice_nick", "favourite_map", "favourite_tribe", "favourite_addon", "avatar"),
            },
        ),
        
    )


admin.site.register(Profile, ProfileAdmin)
