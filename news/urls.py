from django.conf.urls import *
from news.models import Post
from django.views.generic import DetailView
from news.views import NewsList, YearNews, MonthNews

urlpatterns = [ 
     url(r'^(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/(?P<slug>[-\w]+)/$',
        DetailView.as_view(queryset=Post.objects.published(), template_name="news/post_detail.html"),
        name='news_detail'),

     url(r'^(?P<year>\d{4})/(?P<month>[-\w]+)/$',
          MonthNews.as_view(date_field="publish"),
          name='news_archive_month'),

     url(r'^(?P<year>\d{4})/$',
          YearNews.as_view(),
          name='news_archive_year'),
     
     url(r'^$',
         NewsList.as_view(template_name = 'news/post_list.html'),
         name='news_index'),
]
