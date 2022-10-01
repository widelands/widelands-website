from django.conf.urls import *
from django.views.generic import ListView
from news.views import NewsList, YearNews, MonthNews, NewsDetail, CategoryView
from news.feeds import NewsPostsFeed


urlpatterns = [
    url(
        r"^(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/(?P<slug>[-\w]+)/$",
        NewsDetail.as_view(),
        name="news_detail",
    ),
    url(
        r"^(?P<year>\d{4})/(?P<month>[-\w]+)/$",
        MonthNews.as_view(),
        name="news_archive_month",
    ),
    url(r"^(?P<year>\d{4})/$", YearNews.as_view(), name="news_archive_year"),
    url(r"^category/(?P<slug>[-\w]+)/", CategoryView.as_view(), name="category_posts"),
    url(
        r"^$", NewsList.as_view(template_name="news/post_list.html"), name="news_index"
    ),
    # Feed
    url(r"^feed/$", NewsPostsFeed()),
]
