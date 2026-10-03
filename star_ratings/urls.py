from django.urls import re_path

from .views import Rate

urlpatterns = [
    re_path(
        r"(?P<content_type_id>\d+)/(?P<object_id>\d+)/", Rate.as_view(), name="rate"
    ),
]

app_name = "star_ratings"
