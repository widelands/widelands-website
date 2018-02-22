#!/usr/bin/env python -tt
# encoding: utf-8
#

from models import Map
from django.contrib import admin


class MapAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'pub_date']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'author']
    list_filter = ['pub_date']
    readonly_fields = ('uploader', 'nr_players', 'w', 'h', 'minimap', 'file', 'world_name')
    fieldsets = (
        (None, {
            'fields': (('name', 'author'), 'uploader', 'uploader_comment')
        }),
        ('Map properties', {
            'classes': ('collapse',),
            'fields': ('descr', 'hint', 'world_name',
                       ('nr_players', 'w', 'h')
                       )
        }),
        ('Upload information', {
            'classes': ('collapse',),
            'fields': ('minimap', 'file', 'pub_date', 'nr_downloads', 'slug')
        }),
    )
admin.site.register(Map, MapAdmin)
