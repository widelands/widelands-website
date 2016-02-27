#!/usr/bin/env python -tt
# encoding: utf-8
#

from models import Poll
from django.conf.urls import *
import views

info_dict = {
    'queryset': Poll.objects.all()
}

urlpatterns = patterns('', 
    url(r'^$', 'django.views.generic.list_detail.object_list', info_dict, name="wlpoll_archive"),
    url(r'(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict, name="wlpoll_detail"),
    url(r'(?P<object_id>\d+)/vote/$', views.vote, name="wlpoll_vote"),
)

