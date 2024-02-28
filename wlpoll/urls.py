#!/usr/bin/env python -tt
# encoding: utf-8
#

from .models import Poll
from django.urls import *
from . import views
from django.views.generic.dates import ArchiveIndexView

# delete this
info_dict = {"queryset": Poll.objects.all()}

urlpatterns = [
    re_path(
        r"^$",
        ArchiveIndexView.as_view(
            model=Poll, date_field="pub_date", template_name="wlpoll/poll_list.html"
        ),
        name="wlpoll_archive",
    ),
    re_path(r"^(?P<pk>[0-9]+)/$", views.DetailView.as_view(), name="wlpoll_detail"),
    re_path(r"(?P<object_id>\d+)/vote/$", views.vote, name="wlpoll_vote"),
]
