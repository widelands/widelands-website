# -*- coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from pybb.models import Category, Forum, Topic, Post, Read

def delete_selected(modeladmin, request, queryset):
    """ Overwritten default action to delete a post.
    This action uses the delete() method of the post model.
    This ensures also deleting a topic if neccesary, preventing
    index-errors if a topic has no post."""
    for obj in queryset:
        obj.delete()
delete_selected.short_description = 'Delete selected posts'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'forum_count']
    list_per_page = 20
    ordering = ['position']
    search_fields = ['name']

class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'position', 'topic_count']
    list_per_page = 20
    ordering = ['-category']
    search_fields = ['name', 'category__name']
    fieldsets = (
        (None, {
                'fields': ('category', 'name', 'updated')
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields': ('position', 'description', 'moderators')
                }
            ),
        )

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created', 'head', 'is_hidden']
    list_per_page = 20
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['name']
    fieldsets = (
        (None, {
                'fields': ('forum', 'name', 'user', ('created', 'updated'))
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields': (('views',), ('sticky', 'closed'), 'subscribers')
                }
         ),
        )

class PostAdmin(admin.ModelAdmin):
    list_display = ['summary', 'topic', 'user', 'created', 'hidden']
    list_per_page = 20
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['body']
    actions = [delete_selected]
    fieldsets = (
        (None, {
                'fields': ('topic', 'user', 'markup', 'hidden')
                }
         ),
        (_('Additional options'), {
                'classes': ('collapse',),
                'fields' : (('created', 'updated'), 'user_ip' )
                }
         ),
        (_('Message'), {
                'fields': ('body', 'body_html', 'body_text')
                }
         ),
        )

class ReadAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'time']
    list_per_page = 20
    ordering = ['-time']
    date_hierarchy = 'time'
    search_fields = ['user__username', 'topic__name']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Read, ReadAdmin)
