from django.contrib import admin
from notification.models import NoticeType, NoticeSetting, ObservedItem


class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'display', 'description', 'default')


class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notice_type', 'medium', 'send')


class ObserverdItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'notice_type', 'user',)


admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
admin.site.register(ObservedItem, ObserverdItemAdmin)
