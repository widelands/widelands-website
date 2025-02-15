from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from check_input.models import SuspiciousInput
from check_input.models import SuspiciousKeyword


@admin.action(description="Delete selected posts")
def delete_objects(modeladmin, request, queryset):
    for obj in queryset:
        try:
            obj.content_type.get_object_for_this_type(pk=obj.object_id).delete()
        except ObjectDoesNotExist:
            # this post was probably deleted elsewhere
            pass
        obj.delete()


@admin.action(description="Unhide posts and inform subscribers")
def unhide_post(modeladmin, request, queryset):
    for obj in queryset:
        post_obj = obj.content_type.get_object_for_this_type(pk=obj.object_id)
        if obj.content_type.model == "topic":
            # A topic has no function unhide_post(),
            # but the first Post object has it
            # Remember: A topic is hidden if the first post is hidden
            post_obj = obj.content_type.get_object_for_this_type(
                pk=obj.object_id
            ).posts.all()[0]

        post_obj.unhide_post()
        obj.delete()


class SuspiciousInputAdmin(admin.ModelAdmin):
    list_display = ("text", "user", "content_type")
    readonly_fields = (
        "text",
        "content_type",
    )
    exclude = (
        "content_type",
        "object_id",
    )

    actions = [delete_objects, unhide_post]


class SuspiciousKeywordAdmin(admin.ModelAdmin):
    list_display = ("keyword", "description")


admin.site.register(SuspiciousInput, SuspiciousInputAdmin)
admin.site.register(SuspiciousKeyword, SuspiciousKeywordAdmin)
