#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Get acces to additional models which are not set by Django by default.

So Djangos orm is used when changing things, e.g. delete a permission.

"""

from django.contrib import admin
from django.contrib.auth.models import Permission
admin.site.register(Permission)


# Taken from: https://www.djangosnippets.org/snippets/1650/
"""Displays the users which are in a group to /admin/auth/group"""

from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib import admin
from django.core.urlresolvers import reverse


def persons(self):
    return ', '.join(['<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=(x.id,)), x.username) for x in self.user_set.all().order_by('username')])
persons.allow_tags = True

class GroupAdmin(GroupAdmin):
    list_display = ['name', persons]
    list_display_links = ['name']


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
