from django.urls import re_path, include
from . import views
from django_messages.views import compose, reply
from django_messages_wl.forms import ExtendedComposeForm

urlpatterns = [
    re_path(r"^django_messages_wl/get_usernames/", views.get_usernames),
    # Overridden urls to add a custom validator
    re_path(
        r"^compose/$",
        compose,
        {"form_class": ExtendedComposeForm},
        name="messages_compose",
    ),
    re_path(
        r"^compose/(?P<recipient>[\w.@+-]+)/$",
        compose,
        {"form_class": ExtendedComposeForm},
        name="messages_compose_to",
    ),
    re_path(
        r"^reply/(?P<message_id>[\d]+)/$",
        reply,
        {"form_class": ExtendedComposeForm},
        name="messages_reply",
    ),
    # Needs to be after the custom views
    re_path(r"^", include("django_messages.urls")),
]
