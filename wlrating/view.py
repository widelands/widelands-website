#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Game, Rating
from datetime import datetime, timedelta
from wlrating.glicko2 import Glicko_rating

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


@login_required
def score (request):
    # temp constant for testing
    start_date = datetime.strptime('2010/01/01', '%Y/%m/%d')
    end_date= datetime.now()
    delta = end_date - start_date    

    for i in range(delta.days):
        if i % 30 == 0:
            rating_day = start_date + timedelta(days=i)
            rate_a_day(rating_day)

    return render(request, 'wlrating/score.html')

def rate_a_day (date):
    games_to_evaluate = []
    for g in Game.objects.order_by('start_date'):
        if date - timedelta(days = 30) <= g.start_date <= date and temp_clean_before_glicko(g):
                games_to_evaluate.append(temp_clean_before_glicko(g))
    if games_to_evaluate:
        new_rating = Glicko_rating(games_to_evaluate)
        new_rating.evaluate_new_score()

def temp_clean_before_glicko(raw_game_data):
    clean_data = {}
    player_list = raw_game_data.players.split(", ")
    binary_result = raw_game_data.result.split(',')
    
    if len(player_list)>1:
        clean_data['player1'] = player_list[0]
        clean_data['player2'] = player_list[1]
        if binary_result[0] == '1':
            clean_data['result'] = "win"
        else:
            clean_data['result'] = "loss"

        clean_data['date'] = raw_game_data.start_date

        return clean_data
        
