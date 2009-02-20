from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Django builtin / Registration
    (r'^accounts/logout/(next=(?P<next_page>.*))?$', 'django.contrib.auth.views.logout'),
    (r'^accounts/', include('registration.urls')),
                       
    # 3rd party
    (r'^wiki/', include('wiki.urls'), {'is_member': lambda u,g: False}),
    
    # WL specific:
    (r'main/', include('widelands.mainpage.urls')),
)

try:
    from local_urls import *
    urlpatterns += local_urlpatterns
except ImportError:
    pass

