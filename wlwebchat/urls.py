#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.urls import re_path
from .views import webchat

urlpatterns = [
    # Uncomment the next line to enable the admin:
    re_path(r"^$", webchat, name="webchat_index"),
]
