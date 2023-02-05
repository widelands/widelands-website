from django.urls import *
from django.views.generic import ListView
from news.views import NewsList, YearNews, MonthNews, NewsDetail, CategoryView
from news.feeds import NewsPostsFeed


urlpatterns = [
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/(?P<slug>[-\w]+)/$",
        NewsDetail.as_view(),
        name="news_detail",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>[-\w]+)/$",
        MonthNews.as_view(),
        name="news_archive_month",
    ),
    re_path(r"^(?P<year>\d{4})/$", YearNews.as_view(), name="news_archive_year"),
    re_path(r"^category/(?P<slug>[-\w]+)/", CategoryView.as_view(), name="category_posts"),
    re_path(
        r"^$", NewsList.as_view(template_name="news/post_list.html"), name="news_index"
    ),
    # Feed
    re_path(r"^feed/$", NewsPostsFeed()),
]
