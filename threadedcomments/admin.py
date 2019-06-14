from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from threadedcomments.models import ThreadedComment


class ThreadedCommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('content_type', 'object_id')}),
        (_('Parent'), {'fields': ('parent',)}),
        (_('Content'), {'fields': ('user', 'comment')}),
        (_('Meta'), {'fields': ('is_public', 'date_submitted',
                                'date_modified', 'date_approved', 'is_approved')}),
    )
    list_display = ('user', 'date_submitted', 'content_type',
                    'get_content_object', 'parent', '__str__')
    list_filter = ('date_submitted',)
    date_hierarchy = 'date_submitted'
    search_fields = ('comment', 'user__username')


admin.site.register(ThreadedComment, ThreadedCommentAdmin)
