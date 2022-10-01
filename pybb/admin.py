# -*- coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from pybb.models import Category, Forum, Topic, Post, Read, Attachment


def delete_selected(modeladmin, request, queryset):
    """Overwritten Django's default action to delete a post.

    This action uses the delete() method of the post model.
    This ensures also deleting a topic if neccesary, preventing
    index-errors if a topic has only one post.

    """
    for obj in queryset:
        obj.delete()


def unhide_post(modeladmin, request, queryset):
    """Unhide post(s) and inform subscribers."""
    for obj in queryset:
        obj.unhide_post()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "forum_count"]
    list_per_page = 20
    ordering = ["position"]
    search_fields = ["name"]


class ForumAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "position", "topic_count", "moderator_group"]
    list_per_page = 20
    ordering = ["category__position", "position"]
    search_fields = ["name", "category__name"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "name",
                    "updated",
                    "moderator_group",
                )
            },
        ),
        (
            _("Additional options"),
            {
                "description": "Position is the position inside the category. \
            This has effect on ordering in forums overview and the navigation bar.",
                "fields": ("position", "description"),
            },
        ),
    )


class PostInline(admin.TabularInline):
    model = Post
    readonly_fields = (
        "user",
        "markup",
        "created",
    )
    exclude = (
        "created",
        "updated",
        "body",
    )
    ordering = ("-created",)


class TopicAdmin(admin.ModelAdmin):
    list_display = ["name", "forum", "created", "head", "is_hidden"]
    list_per_page = 20
    ordering = ["-created"]
    date_hierarchy = "created"
    search_fields = ["name"]
    inlines = [
        PostInline,
    ]
    fieldsets = (
        (None, {"fields": ("forum", "name", "user", ("created", "updated"))}),
        (
            _("Additional options"),
            {
                "classes": ("collapse",),
                "fields": (
                    ("views",),
                    ("sticky", "closed"),
                ),
            },
        ),
    )


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 0
    exclude = ("hash",)


class PostAdmin(admin.ModelAdmin):
    list_display = ["summary", "topic", "user", "created", "hidden"]
    list_per_page = 20
    ordering = ["-created"]
    date_hierarchy = "created"
    search_fields = ["body", "topic__name"]
    inlines = [
        AttachmentInline,
    ]
    fieldsets = (
        (None, {"fields": ("topic", "user", "markup", "hidden")}),
        (
            _("Date and Time"),
            {"classes": ("collapse",), "fields": (("created", "updated"),)},
        ),
        (_("Message"), {"fields": ("body", "body_html", "body_text")}),
    )

    def get_actions(self, request):
        # Overwrite delete_selected from base class.
        actions = admin.ModelAdmin.get_actions(self, request)
        actions["delete_selected"] = (
            delete_selected,
            "delete_selected",
            "Delete selected posts",
        )
        actions["unhide_post"] = (
            delete_selected,
            "unhide_post",
            "Unhide post and inform subscribers",
        )
        return actions


class ReadAdmin(admin.ModelAdmin):
    list_display = ["user", "topic", "time"]
    list_per_page = 20
    ordering = ["-time"]
    date_hierarchy = "time"
    search_fields = ["user__username", "topic__name"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Read, ReadAdmin)
