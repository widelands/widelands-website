from anti_spam.models import FoundSpam
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType


class FoundSpamAdmin(admin.ModelAdmin):
    list_display = ('spam_text', 'user', 'get_app')
    readonly_fields = ('spam_text', 'user', 'get_app',)
    exclude = ('content_type', 'object_id', )
    # fieldsets = (
    #     (None, {
    #         'description': '<strong>This is just an informational view!</strong>',
    #         'fields': ('spam_text', 'user', 'content_type', 'object_id',)
    #     }),
    # )
    
    def get_app(self, obj):
        app = ContentType.objects.get_for_id(
            obj.content_type_id)

        return '%s/%s' % (app.app_label, app.name)
    get_app.short_description = 'Found in App/Model'

admin.site.register(FoundSpam, FoundSpamAdmin)
