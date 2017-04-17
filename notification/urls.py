from django.conf.urls import url

from notification.views import notices#, mark_all_seen, single

urlpatterns = [
    url(r'^$', notices, name='notification_notices'),
    #url(r'^(\d+)/$', single, name='notification_notice'),
]
