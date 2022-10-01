from django.conf.urls import *
from privacy_policy import views

urlpatterns = [
    url(r"^$", views.privacy_policy, name="privacy_policy"),
    url(r"^(?P<slug>[-\w]+)/", views.privacy_policy, name="policy_translated"),
]
