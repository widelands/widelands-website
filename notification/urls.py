from django.conf.urls import url

from notification.views import notice_settings

urlpatterns = [
    url(r'^$', notice_settings, name='notification_notices'),
]
