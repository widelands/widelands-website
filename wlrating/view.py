#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Game, Participant, Player_Rating, Temporary_user, Season
from decimal import Decimal
from .glicko2 import Glicko_rating
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

            p_data = process_data_from_html(r)

            g = Game.objects.create(
                start_date = r['start_date'],
                game_type = type_to_int(r['game_type']),
                game_map = r['game_map'],
                win_team = p_data['win_team'],
                game_status = 1, #todo when working on user submissions
                game_breaks = 0, #todo when working on user submissions
            )
            g.save()

            for participant in p_data['participations']:               
                tu, is_new_user = Temporary_user.objects.get_or_create(username=participant['user'])

                p = Participant.objects.create(
                    user = tu,
                    game = g,
                    team = participant['team'],
                    submitter = participant['submitter'],
                    tribe = participant['tribe'],
                )
                p.save()

        game_list = []
        for g in Game.objects.order_by('start_date'):
            game_data = {}
            game_data['start_date'] = datetime.strftime(g.start_date, TIME_FORMAT)
            game_data['game_type'] = g.game_type
            game_data['game_map'] = g.game_map
            game_data['win_team'] = g.win_team
            
            game_list.append(game_data)

            tribes_string = ''
            for p in Participant.objects.filter(game = g):
                tribes_string +=  int_to_string(p.tribe) + ','
            
            game_data['tribes'] = tribes_string

        return render(request, 'wlrating/arbiter.html', {'game_list': game_list})

        


@login_required
def score (request):

    #To move to separate section so we don't recalculte the score every time someone look at them
    for tu in Temporary_user.objects.all():
        nb_of_games = 0
        win= 0
        
        for p in Participant.objects.filter(user = tu):
            nb_of_games += 1
            g = Game.objects.get(id = p.game.id)
            win = win + 1  if g.win_team == p.team else win #ugly fix


        s = Season.objects.get(
            name = 'Season I: The season of many builds'
        )

        try:
            pr = Player_Rating.objects.get(
                user = tu,
                rating_type = 1,
            )
        except Player_Rating.DoesNotExist:
            pr = Player_Rating.objects.create(
                user = tu,
                rating_type = 1,
                decimal1 = nb_of_games,
                decimal2 = win,
                decimal3 = Decimal(win/nb_of_games).quantize(Decimal('1.00000')),
                season = s,
            )
            pr.save()
        pr.decimal1 = nb_of_games
        pr.decimal2 = win
        pr.decimal3 = Decimal(win/nb_of_games).quantize(Decimal('1.00000'))
        pr.save()
        


    win_ratio_board = []
    for pr in Player_Rating.objects.order_by('-decimal3').filter(rating_type= 1):
        player_data = {}
        player_data['username'] = pr.user.username
        player_data['nb_of_games'] = int(pr.decimal1)
        player_data['win'] = int(pr.decimal2)
        player_data['win_ratio'] = int(pr.decimal3* 100) 
        win_ratio_board.append(player_data)

    new_rating = Glicko_rating()
    new_rating.evaluate_new_score()

    glicko_board = []
    for pr in Player_Rating.objects.order_by('-decimal1').filter(rating_type= 3):
        player_data = {}
        player_data['username'] = pr.user.username
        player_data['rating'] = int(pr.decimal1)
        player_data['deviation'] = int(pr.decimal2)
        player_data['volatility'] = int(pr.decimal3* 100) 
        glicko_board.append(player_data)

    return render(request, 'wlrating/score.html', {'win_ratio_board' : win_ratio_board, 
                                                   'glicko2_board' : glicko_board})


# data html handling
def process_data_from_html(r):
    results_list = clean_list(r['result'].split(','))
    tribes_list = clean_list(r['tribes'].split(','))
    players_list = clean_list(r['players'].split(','))
    data = {}
    data['participations'] = []

    for num, player in enumerate(players_list):
        print (player, num, tribes_list[num], results_list[0])
        participation = {}
        participation['user'] = player
        participation['team'] = num #to change for bigger team than 1vs1
        participation['submitter'] = False
        participation['tribe'] = type_to_int(tribes_list[num])
        data['participations'].append(participation)

    data['win_team'] = results_list[1] #to change for bigger team than 1vs1
    return data

def clean_list(l):
    for num, i in enumerate(l):
        if isinstance(i, str):
            l[num] = i.strip()

    return l


# Ugly, to fix. Maybe an array?
def type_to_int(word):
    word = word.lower()
    if word == 'autocrat':
        return 1
    if word == 'wood gnome':
        return 2
    if word == 'collectors':
        return 3
    if word == 'empire':
        return 1
    if word == 'barbarian':
        return 2
    if word == 'atlantean':
        return 3
    if word == 'frisian':
        return 4

def int_to_string(tribe):
    if tribe == 1:
        return 'empire'
    if tribe == 2:
        return 'barbarian'
    if tribe == 3:
        return 'atlantean'
    if tribe == 4:
        return 'frisian'

    return str(tribe)