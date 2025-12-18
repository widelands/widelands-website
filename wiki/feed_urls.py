from django.urls import re_path
from django.conf import settings

from wiki.feeds import (
    RssHistoryFeed,
    AtomHistoryFeed,
    RssArticleHistoryFeed,
    AtomArticleHistoryFeed,
)

urlpatterns = [
    re_path(r"^rss/$", RssHistoryFeed(), name="wiki_history_feed_rss"),
    re_path(r"^atom/$", AtomHistoryFeed(), name="wiki_history_feed_atom"),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/rss/$",
        RssArticleHistoryFeed(),
        name="wiki_article_history_feed_rss",
    ),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/atom/$",
        AtomArticleHistoryFeed(),
        name="wiki_article_history_feed_atom",
    ),
]
