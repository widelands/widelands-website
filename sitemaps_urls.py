from django.conf.urls import *

from mainpage.views import mainpage
from django.contrib.sitemaps.views import sitemap
from wiki.sitemap import *
from news.sitemap import *
from pybb.sitemap import *
from wlhelp.sitemap import *

sitemaps = {
    # 'news': NewsSitemap,
    # 'wiki': WikiSitemap,
    # 'forum': ForumSitemap,
    'wlhelp': WlHelpSitemap,
    # 'wlhelptribe': WlHelpTribeSitemap,
    # 'wlhelpware': WlHelpWareSitemap,
    # 'wlhelpworker': WlHelpWorkerSitemap,
    }

urlpatterns = [
    # Creating a sitemap.xml
    #url(r'^encyclopedia/atlanteans/$', views.index, name='encyc_atlanteans'),
    url(r'^$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    ]