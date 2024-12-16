# -*- coding: utf-8 -*-

from django.urls import *
from wiki import views
from django.conf import settings
from django.views.generic import RedirectView
from wiki.feeds import (
    RssHistoryFeed,
    AtomHistoryFeed,
    RssArticleHistoryFeed,
    AtomArticleHistoryFeed,
)
from wiki.models import Article

from tagging.views import TaggedObjectList


urlpatterns = [
    # Redirects
    re_path(
        r"^ChangeLog/",
        RedirectView.as_view(url="/changelog/", permanent=True),
        name="wiki_changelog",
    ),
    # I wanted a true reverse, but it didn't work out
    re_path(
        r"^$",
        RedirectView.as_view(url="/wiki/Main Page", permanent=True),
        name="wiki_index",
    ),
    re_path(r"^preview/$", views.article_preview, name="wiki_preview"),
    re_path(r"^diff/$", views.article_diff, name="wiki_preview_diff"),
    re_path(
        r"^list/$",
        views.article_list,
        name="wiki_list",
    ),
    re_path(r"^trash/list/$", views.trash_list, name="wiki_list_deleted"),
    re_path(r"^history/$", views.history, name="wiki_history"),
    # Feeds
    re_path(r"^feeds/rss/$", RssHistoryFeed(), name="wiki_history_feed_rss"),
    re_path(r"^feeds/atom/$", AtomHistoryFeed(), name="wiki_history_feed_atom"),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/feeds/rss/$",
        RssArticleHistoryFeed(),
        name="wiki_article_history_feed_rss",
    ),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/feeds/atom/$",
        AtomArticleHistoryFeed(),
        name="wiki_article_history_feed_atom",
    ),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/$",
        views.view_article,
        name="wiki_article",
    ),
    re_path(
        r"^trash/edit/(?P<title>" + settings.WIKI_URL_RE + r")/$",
        views.edit_article,
        name="wiki_edit_deleted",
    ),
    re_path(
        r"^(?P<title>" + settings.WIKI_URL_RE + r")/(?P<revision>\d+)/$",
        views.view_article,
        name="wiki_article_revision",
    ),
    re_path(
        r"^edit/(?P<title>" + settings.WIKI_URL_RE + r")/$",
        views.edit_article,
        name="wiki_edit",
    ),
    re_path(
        r"observe/(?P<title>" + settings.WIKI_URL_RE + r")/$",
        views.observe_article,
        name="wiki_observe",
    ),
    re_path(
        r"observe/(?P<title>" + settings.WIKI_URL_RE + r")/stop/$",
        views.stop_observing_article,
        name="wiki_stop_observing",
    ),
    re_path(
        r"^history/(?P<title>" + settings.WIKI_URL_RE + r")/$",
        views.article_history,
        name="wiki_article_history",
    ),
    re_path(
        r"^history/(?P<title>"
        + settings.WIKI_URL_RE
        + r")/changeset/(?P<revision>\d+)/$",
        views.view_changeset,
        name="wiki_changeset",
    ),
    re_path(
        r"^history/(?P<title>"
        + settings.WIKI_URL_RE
        + r")/changeset/(?P<revision_from>\d+)/(?P<revision>\d+)/$",
        views.view_changeset,
        name="wiki_changeset_compare",
    ),
    re_path(
        r"^history/(?P<title>" + settings.WIKI_URL_RE + r")/revert/$",
        views.revert_to_revision,
        name="wiki_revert_to_revision",
    ),
    re_path(
        r"^backlinks/(?P<title>" + settings.WIKI_URL_RE + r")/$",
        views.backlinks,
        name="backlinks",
    ),
    re_path(
        r"^tag_list/(?P<tag>[^/]+(?u))/$",
        TaggedObjectList.as_view(
            queryset=Article.objects.exclude(deleted=True),
            # model=Article,
            allow_empty=True,
            template_name="wiki/tag_view.html",
        ),
        name="article_tag_detail",
    ),
]
