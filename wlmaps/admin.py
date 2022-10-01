#!/usr/bin/env python -tt
# encoding: utf-8
#

from .models import Map
from django.contrib import admin

def delete_selected(modeladmin, request, queryset):
    """Overwritten Django's default action to delete a map.

    This action uses the delete() method of the map model. This ensures
    also deleting the corresponding files (.wmf and .png) of a map.

    """
    for obj in queryset:
        obj.delete()
delete_selected.short_description = 'Delete selected maps'


class MapAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'pub_date']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'author']
    list_filter = ['pub_date']
    readonly_fields = ('uploader', 'nr_players', 'w', 'h', 'minimap', 'file', 'world_name')
    fieldsets = (
        (None, {
            'fields': (('name', 'author'), 'uploader', 'uploader_comment', 'wl_version_after')
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

    def get_actions(self, request):
        # Overwrite delete_selected from base class.
        actions = admin.ModelAdmin.actions[:]
        del actions['delete_selected']
        return actions + [delete_selected]

admin.site.register(Map, MapAdmin)
