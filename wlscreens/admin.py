#!/usr/bin/env python -tt
# encoding: utf-8

from models import Category, Screenshot
from django.contrib import admin

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = [ "name" ]
    list_display = ["name" ]

admin.site.register(Category, CategoryAdmin)

class ScreenshotAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["category"]

admin.site.register(Screenshot, ScreenshotAdmin)

