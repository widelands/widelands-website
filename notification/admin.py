from django.contrib import admin
from notification.models import NoticeType, NoticeSetting, ObservedItem


class NoticeTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'display', 'description', 'default')


class NoticeSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notice_type', 'medium', 'send')


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'notice_type',
                    'added', 'unseen', 'archived')

class ObserverdItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'notice_type', 'user',)
admin.site.register(NoticeType, NoticeTypeAdmin)
admin.site.register(NoticeSetting, NoticeSettingAdmin)
#admin.site.register(Notice, NoticeAdmin)
admin.site.register(ObservedItem, ObserverdItemAdmin)
