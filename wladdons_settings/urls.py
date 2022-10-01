from django.conf.urls import url

from wladdons_settings.views import addon_settings
from . import views

urlpatterns = [
    url(r"^$", views.addon_settings, name="addon_settings"),
]
