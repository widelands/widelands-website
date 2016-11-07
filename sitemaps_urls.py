from django.conf.urls import *

from mainpage.views import mainpage
from django.contrib.sitemaps.views import sitemap
from static_sitemap import StaticViewSitemap
from wiki.sitemap import *
from news.sitemap import *
from pybb.sitemap import *
from wlhelp.sitemap import *
from sphinxdoc.sitemap  import *

sitemaps = {
    'static': StaticViewSitemap,
    'docs': DocumentationSitemap,
    'news': NewsSitemap,
    'wiki': WikiSitemap,
    'forum': ForumSitemap,
    'wlhelptribe': WlHelpTribeSitemap,
    'wlhelpware': WlHelpWareSitemap,
    'wlhelpworker': WlHelpWorkerSitemap,
    'wlhelpbuildings': WlHelpBuildingSitemap,
    }

urlpatterns = [
    # Creating a sitemap.xml
    url(r'^$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap')
    ]
