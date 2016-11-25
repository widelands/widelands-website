# encoding: utf-8

from django.conf.urls import *
from django.views.generic.list import ListView
from sphinxdoc import views
from sphinxdoc import models

app_info = {
    'queryset': models.App.objects.all().order_by('name'),
    'template_object_name': 'app',
}


urlpatterns = [
    url(r'^$', ListView.as_view(), app_info,),
    url(r'^(?P<slug>[\w-]+)/search/$',
        views.search, name='doc-search', ),
    url(r'^(?P<slug>[\w-]+)/_images/(?P<path>.*)$',
        views.images, ),
    url(r'^(?P<slug>[\w-]+)/_source/(?P<path>.*)$',
        views.source, ),
    url(r'^(?P<slug>[\w-]+)/_objects/$',
        views.objects_inventory, name='objects-inv', ),
    url(r'^(?P<slug>[\w-]+)/$',
        views.documentation, {'url': ''}, name='doc-index', ),
    url(r'^(?P<slug>[\w-]+)/(?P<url>(([\w-]+)/)+)$',
        views.documentation, name='doc-detail', ),
]
