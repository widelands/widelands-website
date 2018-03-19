from django.contrib import admin
from news.models import *
from datetime import datetime

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):

    def get_changeform_initial_data(self, request):
        # Set initial value for the ForeignKey field to prevent
        # digging through the users list
        return {'author': request.user,
                'publish': datetime.now(),}

    list_display = ('title', 'publish', 'status')
    list_filter = ('publish', 'categories', 'status')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields':(('title', 'slug'), 'body', ('publish', 'categories',), )
        }),
        ('More options', {
            'classes': ('collapse',),
            'fields': ('author', ('status', 'allow_comments',), 'tease', 'tags')
        }),
    )

admin.site.register(Post, PostAdmin)
