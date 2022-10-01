from django.contrib import admin
from notification.models import NoticeType, NoticeSetting, ObservedItem
from django.utils.translation import ugettext_lazy as _


class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "display", "description", "default")


class NoticeSettingAdmin(admin.ModelAdmin):
    search_fields = [
        "user__username",
    ]
    list_display = ("user", "notice_type", "medium", "send")


class ObserverdItemAdmin(admin.ModelAdmin):
    readonly_fields = ("observed_object", "content_type", "object_id")
    search_fields = ["user__username", "notice_type__label"]
    list_display = ("user", "notice_type", "content_type", "get_content_object")
    fieldsets = (
        (None, {"fields": ("user",)}),
        (
            _("Observed object"),
            {"fields": ("observed_object", "content_type", "object_id")},
        ),
        (_("Settings"), {"fields": ("added", "notice_type", "signal")}),
    )


admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(ObservedItem, ObserverdItemAdmin)
