from django.urls import re_path, include
from . import views

urlpatterns = [
    re_path(r"^django_messages_wl/get_usernames/", views.get_usernames),
    # Overridden urls to add custom validators and the spam check
    re_path(r"^compose/$", views.compose, name="messages_compose"),
    re_path(
        r"^compose/(?P<recipient>[\w.@+-]+)/$",
        views.compose,
        name="messages_compose_to",
    ),
    re_path(r"^reply/(?P<message_id>[\d]+)/$", views.reply, name="messages_reply"),
    # Needs to be after the custom views
    re_path(r"^", include("django_messages.urls")),
]
