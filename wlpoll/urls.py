#!/usr/bin/env python -tt
# encoding: utf-8
#

from models import Poll
from django.conf.urls import *
from . import views
from django.views.generic.dates import ArchiveIndexView

#delete this
info_dict = {
    'queryset': Poll.objects.all()
}

urlpatterns = [
    url(r'^$', ArchiveIndexView.as_view(model=Poll,date_field="pub_date", template_name="wlpoll/poll_list.html"),name="wlpoll_archive"),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='wlpoll_detail'),
    url(r'(?P<object_id>\d+)/vote/$', views.vote, name="wlpoll_vote"),
]

