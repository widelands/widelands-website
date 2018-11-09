#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.shortcuts import render
from models import Availabilities
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, timedelta

###########
# Options #
###########
TIME_FORMAT = '%Y-%m-%dT%H'

#########
# Views #
#########
@login_required
def scheduling_main (request):
    return render(request, 'wlscheduling/main.html')

@login_required
def scheduling_find (request):
    current_user = request.user
    other_users_availabilities = {}
    for a in Availabilities.objects.exclude(user=current_user).order_by('avail_time'):
        user_utc_dt_avail_time = a.avail_time
        if datetime.now() < user_utc_dt_avail_time:
            other_user = a.user
            current_user_timezone = current_user.wlprofile.time_zone
            user_dt_avail_time = user_utc_dt_avail_time + timedelta(hours= current_user_timezone)
            user_string_avail_time = datetime.strftime(user_dt_avail_time, TIME_FORMAT)
                
            if not other_user.username in other_users_availabilities:
                other_users_availabilities[other_user.username] = []
            other_users_availabilities[other_user.username].append(user_string_avail_time)
    return render(request, 'wlscheduling/find.html', {'other_users_availabilities': json.dumps(other_users_availabilities)})

@login_required
def scheduling(request):
    current_user = request.user
    current_user_availabilities = []
    user_timezone = current_user.wlprofile.time_zone
        
    # Update of user's availabilities when post mode
    if request.method == 'POST':
        request_avail_times = []
        for r in request.POST:
            if r != "csrfmiddlewaretoken":
                request_avail_times.append(request.POST[r])


        current_user_availabilities = []
        for avail_time in request_avail_times:
            dt_avail_time = datetime.strptime(avail_time, TIME_FORMAT)
            utc_dt_avail_time =  dt_avail_time + timedelta(hours= - user_timezone)

            # We append the string to the list because apparently datetime objects cannot be stored in a list?
            utc_string_avail_time = datetime.strftime(utc_dt_avail_time, TIME_FORMAT)
            current_user_availabilities.append(utc_string_avail_time)
        
        
        for request_avail_time in request_avail_times:
            dt_avail_time = datetime.strptime(request_avail_time, TIME_FORMAT)
            # Actual change of timezone, we got back to UTC
            utc_dt_avail_time =  dt_avail_time + timedelta(hours= - user_timezone)
            avail_time_already_exist = False
            for a in Availabilities.objects.filter(user=current_user, avail_time=utc_dt_avail_time):
                avail_time_already_exist = True
            
            if not avail_time_already_exist:
                a = Availabilities.objects.create(
                    user=current_user,
                    avail_time=utc_dt_avail_time
                )
                a.save()
        
        # We remove any previously stored date that is not present in the request anymore
        for a in Availabilities.objects.filter(user=current_user):
            utc_dt_avail_time = a.avail_time
            to_remove = True
            for utc_string_avail_time in current_user_availabilities:
                request_utc_dt_avail_time = datetime.strptime(utc_string_avail_time, TIME_FORMAT)
                if utc_dt_avail_time == request_utc_dt_avail_time:
                    to_remove = False
            if to_remove:
                a.delete()

        

    current_user_availabilities = []
    for a in Availabilities.objects.filter(user=current_user).order_by('avail_time'):
        utc_dt_avail_time = a.avail_time
        # We display the time with current user timezone
        dt_avail_time = utc_dt_avail_time + timedelta(hours=user_timezone)
        string_avail_time = datetime.strftime(dt_avail_time, TIME_FORMAT)
        current_user_availabilities.append(string_avail_time)

    other_users_availabilities = {}
    for current_user_a in Availabilities.objects.filter(user=current_user).order_by('avail_time'):
        current_user_utc_dt_avail_time = current_user_a.avail_time
        for a in Availabilities.objects.filter(avail_time=current_user_utc_dt_avail_time).exclude(user=current_user).order_by('avail_time'):
            user_utc_dt_avail_time = a.avail_time
            other_user = a.user
            current_user_timezone = current_user.wlprofile.time_zone
            user_dt_avail_time = user_utc_dt_avail_time + timedelta(hours= current_user_timezone)
            user_string_avail_time = datetime.strftime(user_dt_avail_time, TIME_FORMAT)
             
            if not other_user.username in other_users_availabilities:
                other_users_availabilities[other_user.username] = []
            other_users_availabilities[other_user.username].append(user_string_avail_time)


    return render(request, 'wlscheduling/scheduling.html', {'current_user_availabilities': json.dumps(current_user_availabilities),
'other_users_availabilities': json.dumps(other_users_availabilities)})