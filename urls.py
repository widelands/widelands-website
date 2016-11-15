from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from mainpage.views import mainpage

from news.feeds import NewsPostsFeed
from django.views.generic.base import RedirectView
from django.contrib.syndication.views import Feed
from registration.backends.hmac.views import RegistrationView
from mainpage.forms import RegistrationWithCaptchaForm

urlpatterns = [
    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    # Django builtin / Registration
    # overwrite registration with own implementation
    url (r'^accounts/register/$', RegistrationView.as_view(form_class=RegistrationWithCaptchaForm), name='registration_register'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url('^', include('django.contrib.auth.urls')),
    
    # Feed for Mainpage
    url (r'^feeds/news/$', NewsPostsFeed()),

    # Formerly 3rd party
    url (r'^notification/', include('notification.urls')),

    # (r'^stats/', include('simplestats.urls')),
    url (r'^messages/', include('django_messages.urls')),
    url (r'^threadedcomments/', include('threadedcomments.urls')),
#    url(r'^articles/comments/', include('django_comments.urls')),

    # Redirect old urls to docs to docs/wl
    url(r'^docs/$', RedirectView.as_view( url='/docs/wl', permanent=True ), name='docs'),
    url (r'^docs/', include('sphinxdoc.urls')),
        
    # 3rd party, modified for widelands
    url (r'^wiki/', include('wiki.urls')),
    url (r'^news/', include('news.urls')),
    url (r'^forum/', include('pybb.urls')),

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
]

try:
    from local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

handler500 = 'mainpage.views.custom_http_500'
