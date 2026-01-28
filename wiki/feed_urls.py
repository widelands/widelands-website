from django.urls import re_path
from django.conf import settings

from wiki.feeds import (
    WikiHistoryFeed,
    WikiArticleHistoryFeed,
)

urlpatterns = [
    re_path(r"^atom/$", WikiHistoryFeed(), name="wiki_history_feed"),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/$",
        WikiArticleHistoryFeed(),
        name="wiki_article_history_feed",
    ),
]
