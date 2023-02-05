from django.urls import *
from privacy_policy import views

urlpatterns = [
    re_path(r"^$", views.privacy_policy, name="privacy_policy"),
    re_path(r"^(?P<slug>[-\w]+)/", views.privacy_policy, name="policy_translated"),
]
