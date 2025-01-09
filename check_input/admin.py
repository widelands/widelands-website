from django.core.exceptions import ObjectDoesNotExist

from check_input.models import SuspiciousInput
from django.contrib import admin


@admin.action(description="Delete selected posts")
def delete_objects(modeladmin, request, queryset):
    for obj in queryset:
        try:
            obj.content_type.get_object_for_this_type(pk=obj.object_id).delete()
        except ObjectDoesNotExist:
            # this post was probably already deleted
            pass
        obj.delete()


@admin.action(description="Unhide posts and inform subscribers")
def unhide_post(modeladmin, request, queryset):
    for obj in queryset:
        obj.content_type.get_object_for_this_type(pk=obj.object_id).unhide_post()
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


admin.site.register(SuspiciousInput, SuspiciousInputAdmin)
