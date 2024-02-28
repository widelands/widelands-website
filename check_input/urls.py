from django.urls import *
from check_input import views

urlpatterns = [
    re_path(r"^$", views.moderate_info, name="found_spam"),
]
