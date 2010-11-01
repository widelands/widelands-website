#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: ../../urls.py
#
# Created by Holger Rapp on 2009-02-26.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django.conf.urls.defaults import *
from views import * 

urlpatterns= patterns('',
    # Detail pages                
    url(r'^(?P<tribe>\w+)/wares/(?P<ware>[^/]+)/$', ware_details, name="help_ware_details"),
    url(r'^(?P<tribe>\w+)/buildings/(?P<building>[^/]+)/$', building_details, name="help_building_details"),
    url(r'^(?P<tribe>\w+)/workers/(?P<worker>[^/]+)/$', worker_details, name="help_ware_details"),

    url(r'^(?P<tribe>\w+)/workers/$', workers, name="help_workers"),
    url(r'^(?P<tribe>\w+)/wares/$', wares, name="help_wares"),
    url(r'^(?P<tribe>\w+)/buildings/$', buildings, name="help_buildings"),
)
