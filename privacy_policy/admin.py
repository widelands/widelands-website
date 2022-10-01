# -*- coding: utf-8 -*-


from django.contrib import admin
from privacy_policy.models import PrivacyPolicy


class PrivacyPolicyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("language",)}
    list_display = ("language",)


admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
