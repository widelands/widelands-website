from django.conf.urls import url

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
    url(
        r"^$",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    )
]
