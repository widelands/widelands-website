from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# 3rd party
import wiki.urls

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),


    # Django builtin
    # (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/(next=(?P<next_page>.*))?$', 'django.contrib.auth.views.logout'),
    (r'^accounts/', include('registration.urls')),
                       
    # 3rd party
    (r'^wiki/', include(wiki.urls)),
    
    # WL specific:
    (r'main/', include('widelands.mainpage.urls')),
)

try:
    from local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

