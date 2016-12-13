#!/usr/bin/env python -tt
# encoding: utf-8

from models import Event
from django.contrib import admin


class EventAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'start_date']
    list_filter = ['start_date']

admin.site.register(Event, EventAdmin)
