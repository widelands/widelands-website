from django.conf.urls import *
from django_messages.urls import urlpatterns
from . import views


urlpatterns += [
    url(r"^django_messages_wl/get_usernames/", views.get_usernames),
]
