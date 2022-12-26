from django.conf.urls import *
from . import views
from django_messages.views import compose, reply
from django_messages_wl.forms import ExtendedComposeForm

urlpatterns = [
    url(r"^django_messages_wl/get_usernames/", views.get_usernames),
    # Overridden urls to add a custom validator
    url(
        r"^compose/$",
        compose,
        {"form_class": ExtendedComposeForm},
        name="messages_compose",
        ),
    url(
        r"^compose/(?P<recipient>[\w.@+-]+)/$",
        compose,
        {"form_class": ExtendedComposeForm},
        name="messages_compose_to"),
    url(
        r"^reply/(?P<message_id>[\d]+)/$",
        reply,
        {"form_class": ExtendedComposeForm},
        name='messages_reply'),
    # Needs to be after the custom views
    url(r"^", include("django_messages.urls")),
]
