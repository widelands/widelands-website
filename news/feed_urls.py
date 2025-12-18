from django.urls import re_path

from .feeds import NewsPostsFeed

urlpatterns = [
    re_path(r"^", NewsPostsFeed(), name="news_feed"),
]
