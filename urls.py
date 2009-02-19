from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# 3rd party
import wiki.urls

urlpatterns = patterns('',
    # Example:
    (r'main/', include('widelands.mainpage.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^wiki/', include(wiki.urls)),
)

try:
    from local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

