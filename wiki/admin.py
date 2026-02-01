# -*- coding: utf-8 -*-

from django.contrib import admin
from wiki.models import Article, ChangeSet
from wlimages.models import Image
from django.contrib.contenttypes.admin import GenericTabularInline


class InlineImages(GenericTabularInline):
    model = Image
    extra = 0
    fields = ("name", "image", "user", "date_submitted")
    raw_id_fields = ("user",)


class ArticleAdmin(admin.ModelAdmin):
    # Do not show 'Action' to prevent deleting:
    actions = None
    search_fields = ["title"]
    list_display = ("title", "creator", "last_update", "deleted")
    list_filter = ("title",)
    ordering = ["-last_update"]
    fieldsets = ((None, {"fields": ("title", "content", "creator", "deleted")}),)
    raw_id_fields = ("creator",)
    inlines = [InlineImages]


admin.site.register(Article, ArticleAdmin)


class ChangeSetAdmin(admin.ModelAdmin):
    search_fields = ["old_title"]
    list_display = (
        "article",
        "old_title",
        "editor",
        "reverted",
        "modified",
        "comment",
    )
    list_filter = ("article__title",)
    ordering = ("-modified",)
    fieldsets = (
        ("Article", {"fields": ("article", "editor")}),
        ("Differences", {"fields": ("old_title", "content_diff")}),
        (
            "Other",
            {
                "fields": ("comment", "modified", "revision", "reverted"),
                "classes": ("collapse", "wide"),
            },
        ),
    )
    raw_id_fields = ("editor",)


admin.site.register(ChangeSet, ChangeSetAdmin)
