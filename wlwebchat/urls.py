#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.conf.urls import *
from views import webchat

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^$', webchat, name='webchat_index'),

)

