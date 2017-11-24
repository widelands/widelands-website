from django.conf.urls import *
from check_input import views

urlpatterns = [
    url(r'^$', views.moderate_info, name='found_spam'),
    ]
