#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from .models import Availabilities
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, timedelta

###########
# Options #
###########
TIME_FORMAT = "%Y-%m-%dT%H"
# Availabilities further in the future are ignored
MAX_TIME_AHEAD = timedelta(days=365)


#########
# Views #
#########
@login_required
def scheduling_main(request):
    return render(request, "wlscheduling/main.html")


@login_required
def scheduling_find(request):
    current_user_timezone = timedelta(hours=request.user.wlprofile.time_zone)
    other_users_availabilities = {}
    for a in (
        Availabilities.objects.exclude(user=request.user)
        .filter(avail_time__gt=datetime.utcnow())
        .select_related("user")
        .order_by("avail_time")
    ):
        user_dt_avail_time = a.avail_time + current_user_timezone
        other_users_availabilities.setdefault(a.user.username, []).append(
            datetime.strftime(user_dt_avail_time, TIME_FORMAT)
        )
    return render(
        request,
        "wlscheduling/find.html",
        {"other_users_availabilities": json.dumps(other_users_availabilities)},
    )


@login_required
def scheduling(request):
    current_user = request.user
    user_timezone = timedelta(hours=current_user.wlprofile.time_zone)

    # Update of user's availabilities when post mode
    if request.method == "POST":
        # The request contains all availabilities of the user, in his timezone
        utc_avail_times = set()
        latest_avail_time = datetime.utcnow() + MAX_TIME_AHEAD
        for key, avail_time in request.POST.items():
            if key == "csrfmiddlewaretoken":
                continue
            try:
                utc_dt_avail_time = (
                    datetime.strptime(avail_time, TIME_FORMAT) - user_timezone
                )
            except ValueError:
                return HttpResponseBadRequest("Invalid date")
            if utc_dt_avail_time <= latest_avail_time:
                utc_avail_times.add(utc_dt_avail_time)

        # We remove any previously stored date that is not present in the request anymore
        user_availabilities = Availabilities.objects.filter(user=current_user)
        user_availabilities.exclude(avail_time__in=utc_avail_times).delete()

        # Only new dates in the future are stored
        existing = set(user_availabilities.values_list("avail_time", flat=True))
        now = datetime.utcnow()
        Availabilities.objects.bulk_create(
            Availabilities(user=current_user, avail_time=t)
            for t in utc_avail_times - existing
            if now < t
        )

    current_user_utc_avail_times = list(
        Availabilities.objects.filter(user=current_user)
        .order_by("avail_time")
        .values_list("avail_time", flat=True)
    )
    # We display the time with current user timezone
    current_user_availabilities = [
        datetime.strftime(t + user_timezone, TIME_FORMAT)
        for t in current_user_utc_avail_times
    ]

    other_users_availabilities = {}
    for a in (
        Availabilities.objects.filter(avail_time__in=current_user_utc_avail_times)
        .exclude(user=current_user)
        .select_related("user")
        .order_by("avail_time")
    ):
        other_users_availabilities.setdefault(a.user.username, []).append(
            datetime.strftime(a.avail_time + user_timezone, TIME_FORMAT)
        )

    return render(
        request,
        "wlscheduling/scheduling.html",
        {
            "current_user_availabilities": json.dumps(current_user_availabilities),
            "other_users_availabilities": json.dumps(other_users_availabilities),
        },
    )
