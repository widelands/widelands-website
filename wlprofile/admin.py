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
from models import Profile
from django.contrib.auth.models import User


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_zone', 'location']
    list_per_page = 20
    ordering = ['-user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    fieldsets = (
        (None, {
            'fields': ('user', 'time_zone', 'location')
        }
        ),
        (_('IM'), {
            'classes': ('collapse',),
            'fields': ('jabber', 'icq', 'msn', 'aim', 'yahoo')
        }
        ),
        (_('Additional options'), {
            'classes': ('collapse',),
            'fields': ('site', 'avatar', 'signature', 'show_signatures')
        }
        ),
    )

admin.site.register(Profile, ProfileAdmin)


class UserAdmin(admin.ModelAdmin):
    """Customized admin page for django auth.user.

    Replaces in users list: 'first_name' with 'date_joined' and 'last_name' with
    'is_active'

    """
    list_display = ('username', 'email', 'date_joined',
                    'is_active', 'is_staff')
    ordering = ('-date_joined',)
    
    # Carried over from original to keep the users detail view as is.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
