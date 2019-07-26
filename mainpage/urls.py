from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.contrib.syndication.views import Feed
from django_registration.backends.activation.views import RegistrationView
from mainpage.forms import RegistrationWithCaptchaForm


urlpatterns = [
    # Creating a sitemap.xml
    url(r'^sitemap\.xml/', include('mainpage.sitemap_urls')),
    # Static view of robots.txt
    url(r'^robots\.txt/', TemplateView.as_view(template_name='robots.txt', content_type="text/plain")),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    # Django builtin / Registration
    # overwrite registration with own implementation
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=RegistrationWithCaptchaForm), name='django_registration_register'),
    url(r'^accounts/', include('django_registration.backends.activation.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^ratings/', include('star_ratings.urls', namespace='ratings', app_name='ratings')),
    # Formerly 3rd party
    url(r'^notification/', include('notification.urls')),
    
    url(r'^messages/', include('django_messages_wl.urls')),

    url(r'^threadedcomments/', include('threadedcomments.urls')),

    # Redirect old urls to new documentation
    url(r'^docs/wl/(?P<path>.*)', RedirectView.as_view(url='/documentation/%(path)s', permanent=True), name='docs_wl'),
    url(r'^docs/$', RedirectView.as_view(url='/documentation/index.html', permanent=True), name='docs'),

    # 3rd party, modified for widelands
    url(r'^wiki/', include('wiki.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^forum/', include('pybb.urls')),

    # WL specific:
    url(r'^', include('mainpage.mainpage_urls')),
    url(r'^help/(?P<path>.*)', RedirectView.as_view(url='/encyclopedia/%(path)s',
                                                   permanent=True)),  # to not break old links
    url(r'^encyclopedia/', include('wlhelp.urls')),
    url(r'^webchat/', include('wlwebchat.urls')),
    url(r'^images/', include('wlimages.urls')),
    url(r'^profile/', include('wlprofile.urls')),
    url(r'^search/', include('wlsearch.urls')),
    url(r'^poll/', include('wlpoll.urls')),
    url(r'^maps/', include('wlmaps.urls')),
    url(r'^screenshots/', include('wlscreens.urls')),
    url(r'^ggz/', include('wlggz.urls')),
    url(r'^moderated/', include('check_input.urls')),
    url(r'^scheduling/', include('wlscheduling.urls')),
    url(r'^rating/', include('wlrating.urls')),
    url(r'^privacy/', include('privacy_policy.urls')),
]

try:
    from .local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

handler500 = 'mainpage.views.custom_http_500'
