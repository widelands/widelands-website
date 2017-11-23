from django.conf.urls import *
from anti_spam import views

urlpatterns = [
    url(r'^$', views.moderate_info, name='found_spam'),
    ]
