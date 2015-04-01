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

# A function to correct the image paths to a relative path
# This function could be removed if all old image paths are modified
# to "wlimages/name_of_image.extension"
def correct_image_path(modeladmin, request, queryset):
    for obj in queryset:
        obj.image = "wlimages/%s" % (obj.name)
        obj.save()

class ImageAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ( ('image', 'name'), 'date_submitted', 'url','revision')}),
        (_('Upload data:'), { 'fields': ( 'user', 'editor_ip')}),
        (_('Content object:'), { 'fields': ( 'content_type', 'object_id' )}),
    )
    list_display = ( '__unicode__', 'date_submitted', 'content_type', 'user')
    list_filter = ('date_submitted',)
    date_hierarchy = 'date_submitted'
    search_fields = ('image', 'user__username')
    actions = [correct_image_path]

admin.site.register(Image, ImageAdmin)
