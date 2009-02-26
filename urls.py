from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from widelands.mainpage.views import mainpage

from widelands.news.feeds import NewsPostsFeed
from widelands.wiki.feeds import RssHistoryFeed

feeds = {
    'news': NewsPostsFeed,
    
    # Wiki has it's own set of feeds
}

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Django builtin / Registration
    (r'^accounts/logout/(next=(?P<next_page>.*))?$', 'django.contrib.auth.views.logout'),
    (r'^accounts/', include('registration.urls')),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

    # 3rd party, unmodified
    (r'^notification/', include('notification.urls')),
    # (r'^stats/', include('simplestats.urls')),
    (r'^messages/', include('messages.urls')),
    
                       
    # 3rd party, modified for widelands
    (r'^wiki/', include('wiki.urls')),
    (r'^news/', include('news.urls')),
    (r'^forum/', include('pybb.urls')),
    
    # WL specific:
    url(r'^$', mainpage, name="mainpage"),
)

try:
    from local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

