#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Game, Rating
from datetime import datetime


###########
# Options #
###########
TIME_FORMAT = '%Y-%m-%d'

#########
# Views #
#########
@login_required
def rating_main (request):
    return render(request, 'wlrating/main.html', {'is_super_user': request.user.is_superuser})

@login_required
def arbiter (request):
    if request.user.is_superuser:
        if request.method == 'POST':
            #to remove
            current_user = request.user

            r = request.POST
            g = Game.objects.create(
                    user=current_user, #temp, to remove
                    start_date = r['startDate'],
                    game_type = r['game_type'],
                    game_map = r['game_map'],
                    players = r['players'],
                    result = r['result'],
                    submitter = r['submitter'],
            )
            g.save()
            
        game_list = []
        for g in Game.objects.order_by('start_date'):
            game_data = {}
            game_data['start_date'] = datetime.strftime(g.start_date, TIME_FORMAT)
            game_data['game_type'] = g.game_type
            game_data['game_map'] = g.game_map
            game_data['players'] = g.players
            game_data['result'] = g.result
            game_data['submitter'] = g.submitter
            game_list.append(game_data)

        return render(request, 'wlrating/arbiter.html', {'game_list': game_list})

