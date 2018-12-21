# -*- coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from pybb.models import Category, Forum, Topic, Post, Read


def delete_selected(modeladmin, request, queryset):
    """Overwritten Django's default action to delete a post.

    This action uses the delete() method of the post model.
    This ensures also deleting a topic if neccesary, preventing
    index-errors if a topic has only one post.

    """
    for obj in queryset:
        obj.delete()
delete_selected.short_description = 'Delete selected posts'


def unhide_post(modeladmin, request, queryset):
    """Unhide post(s) and inform subscribers."""
    for obj in queryset:
        obj.unhide_post()
unhide_post.short_description = 'Unhide post and inform subscribers'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'forum_count']
    list_per_page = 20
    ordering = ['position']
    search_fields = ['name']


class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'position', 'topic_count', 'moderator_group']
    list_per_page = 20
    ordering = ['category__position', 'position']
    search_fields = ['name', 'category__name']
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'updated', 'moderator_group',)
        }
        ),
        (_('Additional options'), {
            'description': 'Position is the position inside the category. \
            This has effect on ordering in forums overview and the navigation bar.',
            'fields': ('position', 'description')
        }
        ),
    )
    
class SubscribersInline(admin.TabularInline):
    model = Topic.subscribers.through

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created', 'head', 'is_hidden']
    list_per_page = 20
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('forum', 'name', 'user', ('created', 'updated'))
        }),
        (_('Additional options'), {
            'classes': ('collapse',),
            'fields': (('views',), ('sticky', 'closed'),)
        }),
    )
    inlines = [ SubscribersInline, ]


class PostAdmin(admin.ModelAdmin):
    list_display = ['summary', 'topic', 'user', 'created', 'hidden']
    list_per_page = 20
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['body']
    actions = [delete_selected, unhide_post]
    fieldsets = (
        (None, {
            'fields': ('topic', 'user', 'markup', 'hidden')
        }
        ),
        (_('Additional options'), {
            'classes': ('collapse',),
            'fields': (('created', 'updated'),)
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
