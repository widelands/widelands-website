from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^upload/(?P<content_type>\d+)/(?P<object_id>\d+)/$$', upload, name="images_upload" ),
    url(r'^(?P<image>.+)/(?P<revision>\d+)/$', display, name="images_display" ),
    url(r'^(?P<image>.+)/$', display, { "revision": 1, }, name="images_display" ),
)

