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

from django.conf.urls import *
from .views import *

urlpatterns = [
    url(r"^$", index, name="wlhelp_index"),
    url(
        r"^(?P<tribe>\w+)/wares/(?P<ware>[^/]+)/$",
        ware_details,
        name="wlhelp_ware_details",
    ),
    url(
        r"^(?P<tribe>\w+)/buildings/(?P<building>[^/]+)/$",
        building_details,
        name="wlhelp_building_details",
    ),
    url(
        r"^(?P<tribe>\w+)/workers/(?P<worker>[^/]+)/$",
        worker_details,
        name="wlhelp_worker_details",
    ),
    url(r"^(?P<tribe>\w+)/workers/$", workers, name="wlhelp_workers"),
    url(r"^(?P<tribe>\w+)/wares/$", wares, name="wlhelp_wares"),
    url(r"^(?P<tribe>\w+)/buildings/$", buildings, name="wlhelp_buildings"),
]
