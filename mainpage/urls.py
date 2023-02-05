from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django_registration.backends.activation.views import RegistrationView

from mainpage.forms import LoginTimezoneForm
from mainpage.forms import FormWithCaptcha

admin.autodiscover()

urlpatterns = [
    # Creating a sitemap.xml
    re_path(r"^sitemap\.xml", include("mainpage.sitemap_urls")),
    # Static view of robots.txt
    re_path(
        r"^robots\.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    # Uncomment the next line to enable the admin:
    re_path(r"^admin/", admin.site.urls),
    # Django builtin / Registration
    # overwrite registration with own implementation
    re_path(
        r"^accounts/register/$",
        RegistrationView.as_view(form_class=FormWithCaptcha),
        name="django_registration_register",
    ),
    re_path(r"^accounts/", include("django_registration.backends.activation.urls")),
    re_path(r"^accounts/login/$", LoginView.as_view(authentication_form=LoginTimezoneForm)),
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
    re_path(r"^ratings/", include("star_ratings.urls", namespace="ratings")),
    # Formerly 3rd party
    re_path(r"^notification/", include("notification.urls")),
    # re_path(r"^messages/", include("django_messages_wl.urls")),
    re_path(r"^threadedcomments/", include("threadedcomments.urls")),
    # Redirect old urls to new documentation
    re_path(
        r"^docs/wl/(?P<path>.*)",
        RedirectView.as_view(url="/documentation/%(path)s", permanent=True),
        name="docs_wl",
    ),
    re_path(
        r"^docs/$",
        RedirectView.as_view(url="/documentation/index.html", permanent=True),
        name="docs",
    ),
    # 3rd party, modified for widelands
    re_path(r"^wiki/", include("wiki.urls")),
    re_path(r"^news/", include("news.urls")),
    re_path(r"^forum/", include("pybb.urls")),
    # WL specific:
    re_path(r"^", include("mainpage.mainpage_urls")),
    re_path(
        r"^help/(?P<path>.*)",
        RedirectView.as_view(url="/encyclopedia/%(path)s", permanent=True),
    ),  # to not break old links
    re_path(r"^encyclopedia/", include("wlhelp.urls")),
    re_path(r"^webchat/", include("wlwebchat.urls")),
    re_path(r"^images/", include("wlimages.urls")),
    re_path(r"^profile/", include("wlprofile.urls")),
    re_path(r"^search/", include("wlsearch.urls")),
    re_path(r"^poll/", include("wlpoll.urls")),
    re_path(r"^maps/", include("wlmaps.urls")),
    re_path(r"^screenshots/", include("wlscreens.urls")),
    re_path(r"^ggz/", include("wlggz.urls")),
    re_path(r"^moderated/", include("check_input.urls")),
    re_path(r"^scheduling/", include("wlscheduling.urls")),
    re_path(r"^privacy/", include("privacy_policy.urls")),
    re_path(r"^addons/", include("wladdons_settings.urls")),
    # See: https://github.com/widelands/widelands-website/issues/376
    re_path(
        r"^feeds/news/",
        RedirectView.as_view(url="/news/feed", permanent=True),
    ),
]

try:
    from .local_urls import *

    urlpatterns += local_urlpatterns
except ImportError:
    pass

handler500 = "mainpage.views.custom_http_500"
