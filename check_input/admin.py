from check_input.models import SuspiciousInput
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType


class SuspiciousInputAdmin(admin.ModelAdmin):
    list_display = ("text", "user", "get_app")
    readonly_fields = (
        "text",
        "user",
        "get_app",
    )
    exclude = (
        "content_type",
        "object_id",
    )

    def get_app(self, obj):
        app = ContentType.objects.get_for_id(obj.content_type_id)

        return "%s/%s" % (app.app_label, app.name)

    get_app.short_description = "Found in App/Model"


admin.site.register(SuspiciousInput, SuspiciousInputAdmin)
