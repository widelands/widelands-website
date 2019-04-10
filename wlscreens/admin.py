#!/usr/bin/env python -tt
# encoding: utf-8

from models import Category, Screenshot
from django.contrib import admin


class ScreenshotsInline(admin.TabularInline):
    model = Screenshot
    fields = ('screenshot', 'name', 'comment', 'position')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_display = ['name']
    inlines = [ScreenshotsInline,]

admin.site.register(Category, CategoryAdmin)


class ScreenshotAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['category']
    list_display = ['category', 'name', 'position']

admin.site.register(Screenshot, ScreenshotAdmin)
