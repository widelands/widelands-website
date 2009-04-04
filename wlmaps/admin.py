#!/usr/bin/env python -tt
# encoding: utf-8
#

from models import Map
from django.contrib import admin

class MapAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = [ "name", "author" ]
    list_display = ["name", "author", "pub_date"]
    list_filter = [ "pub_date" ]

admin.site.register(Map, MapAdmin)


