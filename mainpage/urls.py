from django.conf.urls.defaults import *
from widelands.mainpage import views

urlpatterns = patterns('',
    # Example:
    url(r'blah$', (views.mainpage, name="mainpage" )),

)
