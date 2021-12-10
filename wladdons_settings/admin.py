from django.contrib import admin
from wladdons_settings.models import AddonNotice


class AddonNoticeAdmin(admin.ModelAdmin):
    
    search_fields = ['user__username', ]
    list_display = ('label', 'user', 'shouldsend')
    readonly_fields = ('label', 'display', 'description', 'user')


admin.site.register(AddonNotice, AddonNoticeAdmin)
