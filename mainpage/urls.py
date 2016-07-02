from django.conf.urls import *
from widelands.mainpage import views

urlpatterns = patterns('',
    # Example:
    url(r'^$', views.mainpage, name="mainpage" ),

)
