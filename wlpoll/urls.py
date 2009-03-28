#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.conf.urls.defaults import *
import views

urlpatterns = patterns('', 
    url(r'(?P<poll_id>\d+)/$', views.view, name="wlpoll_view"),
    url(r'(?P<poll_id>\d+)/vote/(?P<next>.*)$', views.vote, name="wlpoll_vote"),
)

