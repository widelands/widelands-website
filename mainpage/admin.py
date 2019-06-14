#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Get acces to additional models which are not set by Django by default.

So Djangos orm is used when changing things, e.g. delete a permission.
"""

from django.contrib import admin
from django.contrib.auth.models import Permission
admin.site.register(Permission)


# Adjusted from: https://www.djangosnippets.org/snippets/1650/
"""Displays the users which are in a group to /admin/auth/group.
Displays groups and permissions to admin/auth/user."""

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.core.urlresolvers import reverse


def roles(self):
    # Groups
    text = [x.name for x in self.groups.all()]
    # Permissions
    if self.user_permissions.count():
        text += ['has perm.']
    value = ', '.join(text)
    return value
roles.short_description = 'Groups/Permissions'


def persons(self):
    return ', '.join(['<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=(x.id,)), x.username) for x in self.user_set.all().order_by('username')])
persons.allow_tags = True


def deleted(self):
    return '' if self.wlprofile.deleted==False else 'Yes'
deleted.short_description = 'Deleted himself'


class GroupAdmin(GroupAdmin):
    list_display = ['name', persons]
    list_display_links = ['name']


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login',
                    'is_active', deleted, 'is_staff', roles)
    ordering = ('-date_joined',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
