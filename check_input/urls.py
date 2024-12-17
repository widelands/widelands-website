from django.urls import re_path
from check_input import views

urlpatterns = [
    re_path(r"^$", views.moderate_info, name="found_spam"),
]
