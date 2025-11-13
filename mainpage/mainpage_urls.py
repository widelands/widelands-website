from django.urls import re_path
from mainpage import views

urlpatterns = [
    re_path(r"^$", views.mainpage, name="mainpage"),
    re_path(r"^forum.html", views.honeypot, name="honeypot"),
    re_path(r"^locale/$", views.view_locale),
    re_path(r"^changelog/$", views.changelog, name="changelog"),
    re_path(r"^developers/$", views.developers, name="developers"),
    re_path(r"^legal_notice/$", views.legal_notice, name="legal_notice"),
    re_path(
        r"^legal_notice_thanks/$", views.legal_notice_thanks, name="legal_notice_thanks"
    ),
]
