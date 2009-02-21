from django.conf.urls.defaults import *
from widelands.news import views as news_views


urlpatterns = patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        view=news_views.post_detail,
        name='news_detail'),

    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$',
        view=news_views.post_archive_day,
        name='news_archive_day'),

    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$',
        view=news_views.post_archive_month,
        name='news_archive_month'),

    url(r'^(?P<year>\d{4})/$',
        view=news_views.post_archive_year,
        name='news_archive_year'),

    url(r'^categories/(?P<slug>[-\w]+)/$',
        view=news_views.category_detail,
        name='news_category_detail'),

    url (r'^categories/$',
        view=news_views.category_list,
        name='news_category_list'),

    url (r'^search/$',
        view=news_views.search,
        name='news_search'),

    url(r'^page/(?P<page>\w)/$',
        view=news_views.post_list,
        name='news_index_paginated'),

    url(r'^$',
        view=news_views.post_list,
        name='news_index'),
)
