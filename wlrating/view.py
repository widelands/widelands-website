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
            print (r)
            is_remove_btn = False
            is_calculate_btn= False
            is_create_test_data_btn = False
            is_add_game_btn = False
            for inputs in r:
                if inputs == 'is_remove_btn':
                    is_remove_btn = True
            for inputs in r:
                if inputs == 'is_calculate_btn':
                    is_calculate_btn = True

            for inputs in r:
                if inputs == 'is_create_test_data_btn':
                    is_create_test_data_btn = True

            for inputs in r:
                if inputs == 'is_add_game_btn':
                    is_add_game_btn = True

            if is_remove_btn:
                index = 0
                for g in Game.objects.order_by('start_date'):
                    if index == int(r['is_remove_btn']):
                        for p in Participant.objects.filter(game=g):
                            p.delete()
                        g.delete()
                    index += 1

            if is_calculate_btn:
                calculate_new_scores()

            if is_create_test_data_btn:
                create_test_data()

            if is_add_game_btn :
                p_data = process_data_from_html(r)
                
                g = Game.objects.create(
                    start_date = r.get('start_date'),
                    game_type = type_to_int(r.get('game_type')),
                    game_map = r.get('game_map'),
                    win_team = r.get('result'),
                    game_status = 1, #todo when working on user submissions
                    game_breaks = 0, #todo when working on user submissions
                )
                g.save()
                
                print (p_data)

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

            players = []
            for p in Participant.objects.filter(game = g):
                player = {}
                player['tribe'] =  int_to_string(p.tribe)
                player['username'] = p.user.username
                player['team'] = p.team
                players.append(player)
            
            game_data['tribes'] = tribes_string
            game_data['players']  = players

        return render(request, 'wlrating/arbiter.html', {'game_list': game_list})

        


@login_required
def score (request):
    win_ratio_board = []
    for pr in Player_Rating.objects.order_by('-decimal3').filter(rating_type= 1):
        player_data = {}
        player_data['username'] = pr.user.username
        player_data['nb_of_games'] = int(pr.decimal1)
        player_data['win'] = int(pr.decimal2)
        player_data['win_ratio'] = int(pr.decimal3* 100) 
        win_ratio_board.append(player_data)

    

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
    player_list = {}
    for dict_property, value in r.items():
        if value:
            if "player" in dict_property:
                num = str(dict_property[-1])
                if not num in player_list:
                    player_list[num] = {} 
                player_list[num]['player'] = value
                print (player_list[num])

            if "tribe" in dict_property:
                num = str(dict_property[-1])
                if not num in player_list:
                    player_list[num] = {} 
                player_list[num]['tribe'] = value
                print (player_list[num])
            
            if "team" in dict_property:
                num = str(dict_property[-1])
                if not num in player_list:
                    player_list[num] = {} 
                player_list[num]['team'] = value
                print (player_list[num])

    data = {}
    data['participations'] = []

    print (player_list)

    for dict_property, player in player_list.items():
        participation = {}
        participation['user'] = player_list[dict_property]['player']
        participation['team'] = player_list[dict_property]['team']
        participation['submitter'] = False
        participation['tribe'] = type_to_int(player_list[dict_property]['tribe'])
        data['participations'].append(participation)
    return data

def calculate_new_scores():
    s, created = Season.objects.get_or_create(
        start_date= '2019-06-01',
        end_date='2019-12-01',
        name='Season I: The season of many builds'
    )
    if created:
        s.save()
    
    for tu in Temporary_user.objects.all():
        nb_of_games = 0
        win= 0
        print (tu.username) 

        for p in Participant.objects.filter(user = tu):
            nb_of_games += 1
            g = Game.objects.get(id = p.game.id)
            win = win + 1  if g.win_team == p.team else win

        if nb_of_games > 0:
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
            pr.season = s
            pr.save()

    new_rating = Glicko_rating()
    new_rating.calculate_all_games('Season I: The season of many builds')

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


def create_test_data():
    s, created = Season.objects.get_or_create(
        start_date= '2019-06-01',
        end_date='2019-12-01',
        name='Season I: The season of many builds'
    )
    s.save()

    g1, c1 = Game.objects.get_or_create(
        start_date = '2019-08-08',
        game_type = 1,
        game_map = 'Crater',
        win_team = 1,
        game_status = 1, #todo when working on user submissions
        game_breaks = 0, #todo when working on user submissions
    )
    if c1:
        g1.save()

    g2, c2 = Game.objects.get_or_create(
        start_date = '2019-08-08',
        game_type = 1,
        game_map = 'Ice war',
        win_team = 1,
        game_status = 1, #todo when working on user submissions
        game_breaks = 0, #todo when working on user submissions
    )
    if c2:
        g2.save()

    g3, c3 = Game.objects.get_or_create(
        start_date = '2019-08-08',
        game_type = 1,
        game_map = 'Sea',
        win_team = 1,
        game_status = 1, #todo when working on user submissions
        game_breaks = 0, #todo when working on user submissions
    )
    if c3:
        g3.save()

    tu1, c4 = Temporary_user.objects.get_or_create(
        username = 'main_player'
    )
    if c4:
        tu1.save()
    tu2, c5 = Temporary_user.objects.get_or_create(
        username = 'looser'
    )
    if c5:
        tu2.save()
    tu3, c6 = Temporary_user.objects.get_or_create(
        username = 'winner1'
    )
    if c6:
        tu3.save()
    tu4, c7 = Temporary_user.objects.get_or_create(
        username = 'winner2'
    )
    if c7:
        tu4.save()

    p1, c8 = Participant.objects.get_or_create(
        user = tu1,
        game = g1,
        team = 1,
        submitter = False,
        tribe = 1,
    )
    p2, c9 = Participant.objects.get_or_create(
        user = tu2,
        game = g1,
        team = 0,
        submitter = False,
        tribe = 1,
    )
    p3, c10 = Participant.objects.get_or_create(
        user = tu1,
        game = g2,
        team = 0,
        submitter = False,
        tribe = 1,
    )
    p4, c11 = Participant.objects.get_or_create(
        user = tu3,
        game = g2,
        team = 1,
        submitter = False,
        tribe = 1,
    )
    p5, c12 = Participant.objects.get_or_create(
        user = tu1,
        game = g3,
        team = 0,
        submitter = False,
        tribe = 1,
    )
    p6, c13 = Participant.objects.get_or_create(
        user = tu4,
        game = g3,
        team = 1,
        submitter = False,
        tribe = 1,
    )
    if c8:
        p1.save()
    if c9:
        p2.save()
    if c10:
        p3.save()
    if c11:
        p4.save()
    if c12:
        p5.save()
    if c13:
        p6.save()
    pr1, c14 = Player_Rating.objects.get_or_create(
        user = tu1,
        rating_type= 3,
        decimal1 = 1500,
        decimal2 = 200,
        decimal3 = 0.06,
        season = s,
    )
    pr2, c15 = Player_Rating.objects.get_or_create(
        user = tu2,
        rating_type= 3,
        decimal1 = 1400,
        decimal2 = 30,
        decimal3 = 0.06,
        season = s,
    )
    pr3, c16 = Player_Rating.objects.get_or_create(
        user = tu3,
        rating_type= 3,
        decimal1 = 1550,
        decimal2 = 100,
        decimal3 = 0.06,
        season = s,
    )
    pr4, c17 = Player_Rating.objects.get_or_create(
        user = tu4,
        rating_type= 3,
        decimal1 = 1700,
        decimal2 = 300,
        decimal3 = 0.06,
        season = s,
    )
    if c14:
        pr1.save()
    if c15:
        pr2.save()
    if c16:
        pr3.save()
    if c17:
        pr4.save()