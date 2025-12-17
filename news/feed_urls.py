from django.urls import re_path
from django.views.generic import RedirectView

from news.feeds import NewsPostsFeed

urlpatterns = [
    re_path(r"", NewsPostsFeed()),
]
