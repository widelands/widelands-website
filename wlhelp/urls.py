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

from django.urls import re_path
from .views import (
    index,
    ware_details,
    building_details,
    worker_details,
    workers,
    wares,
    buildings,
)

urlpatterns = [
    re_path(r"^$", index, name="wlhelp_index"),
    re_path(
        r"^(?P<tribe>\w+)/wares/(?P<ware>[^/]+)/$",
        ware_details,
        name="wlhelp_ware_details",
    ),
    re_path(
        r"^(?P<tribe>\w+)/buildings/(?P<building>[^/]+)/$",
        building_details,
        name="wlhelp_building_details",
    ),
    re_path(
        r"^(?P<tribe>\w+)/workers/(?P<worker>[^/]+)/$",
        worker_details,
        name="wlhelp_worker_details",
    ),
    re_path(r"^(?P<tribe>\w+)/workers/$", workers, name="wlhelp_workers"),
    re_path(r"^(?P<tribe>\w+)/wares/$", wares, name="wlhelp_wares"),
    re_path(r"^(?P<tribe>\w+)/buildings/$", buildings, name="wlhelp_buildings"),
]
