from django.conf.urls import *
from .views import *

urlpatterns = [
    url(r'^upload/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<next>.*)$',
        upload, name='wlimages_upload'),
    url(r'^(?P<image>.+)/(?P<revision>\d+)/$', display, name='images_display'),
    url(r'^(?P<image>.+)/$', display,
        {'revision': 1, }, name='images_display'),
]
