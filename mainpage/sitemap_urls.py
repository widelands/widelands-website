from django.urls import re_path

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from wiki.sitemap import *
from news.sitemap import *
from pybb.sitemap import *
from wlhelp.sitemap import *


sitemaps = {
    "static": StaticViewSitemap,
    "news": NewsSitemap,
    "wiki": WikiSitemap,
    "forum": ForumSitemap,
    "wlhelptribe": WlHelpTribeSitemap,
    "wlhelpware": WlHelpWareSitemap,
    "wlhelpworker": WlHelpWorkerSitemap,
    "wlhelpbuildings": WlHelpBuildingSitemap,
}

urlpatterns = [
    # Creating a sitemap.xml
    re_path(
        r"^$",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    )
]
