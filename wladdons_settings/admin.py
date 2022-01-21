from django.contrib import admin
from wladdons_settings.models import AddonNoticeUser
from wladdons_settings.models import AddonNoticeType


class AddonNoticeUserAdmin(admin.ModelAdmin):

    search_fields = ['user__username', ]
    list_display = ('notice_type', 'user', 'shouldsend')


class AddonNoticeTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('display',)}

    list_display = ('display', 'description', 'send_default', 'author_related_default')


admin.site.register(AddonNoticeUser, AddonNoticeUserAdmin)
admin.site.register(AddonNoticeType, AddonNoticeTypeAdmin)
