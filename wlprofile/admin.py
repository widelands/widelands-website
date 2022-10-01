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
    list_display = ["user", "time_zone", "location", "deleted"]
    list_per_page = 20
    ordering = ["-user"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    fieldsets = (
        (None, {"fields": ("user", "time_zone", "location")}),
        (
            _("IM"),
            {
                "classes": ("collapse",),
                "fields": ("jabber", "icq", "msn", "aim", "yahoo"),
            },
        ),
        (
            _("Additional options"),
            {
                "classes": ("collapse",),
                "fields": ("site", "avatar", "signature", "show_signatures"),
            },
        ),
    )


admin.site.register(Profile, ProfileAdmin)
