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
from .models import Image


def delete_with_file(modeladmin, request, queryset):
    for obj in queryset:
        storage = obj.image.storage
        storage.delete(obj.image)
        obj.delete()


delete_with_file.short_description = "Delete Image including File"


class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ("content_object", "content_type", "object_id")
    list_display = ("__str__", "date_submitted", "content_type", "user")
    list_filter = ("date_submitted",)
    date_hierarchy = "date_submitted"
    search_fields = ("image", "user__username")
    actions = [delete_with_file]
    fieldsets = (
        (None, {"fields": ("image", "name", "date_submitted", "revision")}),
        (_("Uploaded by:"), {"fields": ("user",)}),
        (
            _("Content object:"),
            {"fields": (("content_type", "content_object"), "object_id")},
        ),
    )


admin.site.register(Image, ImageAdmin)
