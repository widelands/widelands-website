#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: images/admin.py
#
# Created by Holger Rapp on 2009-03-01.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import Image

class ImageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('content_type', 'object_id')}),
        (_('Content'), {'fields': ('user', 'image', 'revision', 'name')}),
        (_('Meta'), {'fields': ('date_submitted', 'editor_ip')}),
    )
    list_display = ('user', 'date_submitted', 'content_type', 'get_content_object', '__unicode__')
    list_filter = ('date_submitted',)
    date_hierarchy = 'date_submitted'
    search_fields = ('image', 'user__username')

admin.site.register(Image, ImageAdmin)
