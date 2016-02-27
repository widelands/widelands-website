#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from models import Map
from views import *

urlpatterns = patterns('',
                       url(r'^$', index, name='wlmaps_index'),
                       url(r'^upload/$', upload, name='wlmaps_upload'),

                       url(r'^(?P<map_slug>[-\w]+)/$',
                           view, name='wlmaps_view'),
                       url(r'^(?P<map_slug>[-\w]+)/edit_comment/$',
                           edit_comment, name='wlmaps_edit_comment'),
                       url(r'^(?P<map_slug>[-\w]+)/download/$',
                           download, name='wlmaps_download'),

                       url(r'^(?P<map_slug>[-\w]+)/rate/$',
                           rate, name='wlmaps_rate'),
                       )
