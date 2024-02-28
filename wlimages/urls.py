from django.urls import *
from .views import *

urlpatterns = [
    re_path(
        r"^upload/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<next>.*)$",
        upload,
        name="wlimages_upload",
    ),
    re_path(r"^(?P<image>.+)/(?P<revision>\d+)/$", display, name="images_display"),
    re_path(
        r"^(?P<image>.+)/$",
        display,
        {
            "revision": 1,
        },
        name="images_display",
    ),
]
