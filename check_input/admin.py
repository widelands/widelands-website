from check_input.models import SuspiciousInput
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType


@admin.action(description="Delete selected posts")
def delete_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.content_type.get_object_for_this_type(pk=obj.object_id).delete()
        obj.delete()

@admin.action(description="Unhide posts and inform subscribers")
def unhide_post(modeladmin, request, queryset):
    for obj in queryset:
        obj.content_type.get_object_for_this_type(pk=obj.object_id).unhide_post()
        obj.delete()

class SuspiciousInputAdmin(admin.ModelAdmin):
    list_display = ("text", "user", "get_app", "object_id")
    readonly_fields = (
        "text",
        "user",
        "get_app",
    )
    exclude = (
        "content_type",
        "object_id",
    )

    actions = [delete_objects, unhide_post]

    def get_app(self, obj):
        app = ContentType.objects.get_for_id(obj.content_type_id)

        return "%s/%s" % (app.app_label, app.name)

    get_app.short_description = "Found in App/Model"


admin.site.register(SuspiciousInput, SuspiciousInputAdmin)
