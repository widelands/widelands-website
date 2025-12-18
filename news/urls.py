from django.urls import re_path
from django.views.generic import RedirectView

from news.views import NewsList, YearNews, MonthNews, NewsDetail, CategoryView


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
    re_path(
        r"^category/(?P<slug>[-\w]+)/", CategoryView.as_view(), name="category_posts"
    ),
    re_path(
        r"^$", NewsList.as_view(template_name="news/post_list.html"), name="news_index"
    ),
    # Feeds are handled in feed_urls.py to have the base path '/feeds/*' for all feeds
    # Redirect old feed urls
    re_path(
        r"^feed/$",
        RedirectView.as_view(url="/feeds/news", permanent=True),
    ),
]
