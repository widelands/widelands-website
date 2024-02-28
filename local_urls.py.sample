from django.urls import *
from django.conf import settings
from django.views.static import serve
from os import path
from documentation.views import dirhtml_view

# Don't use this file on the server!

local_urlpatterns = [
    # Files uploaded by users
    re_path(r'^wlmedia/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
        name='static_media'),
    # Static files if DEBUG=False. Use the 'collectstatic' command to fetch them
    re_path(r'^static/(?P<path>.*)$',
        serve,
        {'document_root': settings.STATIC_ROOT},
        name='static_media_collected'),
    # HTML documentation created by ./manage.py create_docs
    re_path(r'^documentation/(?P<folder_name>[\w*-?\w*]*)/$', dirhtml_view),
    re_path(r'^documentation/$', dirhtml_view),
    re_path(r'^documentation/(?P<path>.*)$',
        serve,
        {'document_root': path.join(
          settings.MEDIA_ROOT, 'documentation/html/')}
        )
]
