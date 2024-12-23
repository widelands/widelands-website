from django.urls import re_path

from wladdons_settings.views import addon_settings
from . import views

urlpatterns = [
    re_path(r"^$", views.addon_settings, name="addon_settings"),
]
