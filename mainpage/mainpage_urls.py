from django.conf.urls import *
from mainpage import views

urlpatterns = [
    url(r"^$", views.mainpage, name="mainpage"),
    url(r"^locale/$", views.view_locale),
    url(r"^changelog/$", views.changelog, name="changelog"),
    url(r"^developers/$", views.developers, name="developers"),
    url(r"^legal_notice/$", views.legal_notice, name="legal_notice"),
    url(
        r"^legal_notice_thanks/$", views.legal_notice_thanks, name="legal_notice_thanks"
    ),
]
