from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from mainpage.views import mainpage

from news.feeds import NewsPostsFeed
from wiki.feeds import RssHistoryFeed
from django.views.generic.base import RedirectView
from django.contrib.syndication.views import Feed
feeds = {
    'news': NewsPostsFeed,

    # Wiki has it's own set of feeds
}

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    # Django builtin / Registration
    # overwrite registration with own implementation
    url (r'^accounts/register/$', 'mainpage.views.register', name='registration_register'),
    (r'^accounts/', include('registration.backends.hmac.urls')),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.Feed', {'feed_dict': feeds}),

    # 3rd party, unmodified
#    (r'^notification/', include('notification.urls')), #replaced with next
    url(r"^notifications/", include("pinax.notifications.urls")),

    # (r'^stats/', include('simplestats.urls')),
    (r'^messages/', include('django_messages.urls')),
#    (r'^threadedcomments/', include('threadedcomments.urls')), #replaced with next
    url(r'^articles/comments/', include('django_comments.urls')),
    
#    (r'^docs/', include('sphinxdoc.urls')),

    # 3rd party, modified for widelands
    (r'^wiki/', include('wiki.urls')),
    (r'^news/', include('news.urls')),
    (r'^forum/', include('pybb.urls')),

    # WL specific:
    url(r'^$', mainpage, name="mainpage"),
    url(r'^changelog/$', "mainpage.views.changelog", name="changelog"),
    url(r'^developers/$', "mainpage.views.developers", name="developers"),
    url(r'^legal_notice/$', "mainpage.views.legal_notice", name="legal_notice"),
    url(r'^legal_notice_thanks/$', "mainpage.views.legal_notice_thanks", name="legal_notice_thanks"),
    url(r'^help/(?P<path>.*)', RedirectView.as_view( url= "/encyclopedia/%(path)s" , permanent=True)), # to not break old links
    url(r'^encyclopedia/', include("wlhelp.urls")),
    url(r'^webchat/', include("wlwebchat.urls")),
    url(r'^images/', include("wlimages.urls")),
    url(r'^profile/', include("wlprofile.urls")),
    url(r'^search/', include("wlsearch.urls")),
    url(r'^poll/', include("wlpoll.urls")),
    url(r'^maps/', include("wlmaps.urls")),
    url(r'^screenshots/', include("wlscreens.urls")),
    url(r'^ggz/', include("wlggz.urls")),
)

try:
    from local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

