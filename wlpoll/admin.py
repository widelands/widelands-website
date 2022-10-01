#!/usr/bin/env python -tt
# encoding: utf-8
#

from .models import Poll, Choice
from django.contrib import admin


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 10


class PollAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

    search_fields = ["name"]
    list_display = ["name", "pub_date"]
    list_filter = ["pub_date"]


admin.site.register(Poll, PollAdmin)
