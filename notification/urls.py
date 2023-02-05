from django.urls import re_path

from notification.views import notice_settings

urlpatterns = [
    re_path(r"^$", notice_settings, name="notification_notices"),
]
