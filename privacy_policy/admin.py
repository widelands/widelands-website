# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from privacy_policy.models import PrivacyPolicy


class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('language',)


admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
