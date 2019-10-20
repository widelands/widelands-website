#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Game, Participant, Player_Rating, Rating_user, Season, Tribe, Map, GameType
from decimal import Decimal
from .glicko2 import Glicko_rating
from datetime import datetime
from django.http import HttpResponse
import json


###########
# Options #
###########
TIME_FORMAT = '%Y-%m-%d'

#########
# Views #
#########
@login_required
def rating_main(request):
    return render(request, 'wlrating/main.html', {'is_super_user': request.user.is_superuser})


@login_required
def arbiter(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            # to remove
            current_user = request.user

            r = request.POST

            p_data = process_data_from_html(r)
            game_type = GameType.objects.get(name=r.get('game_type'))
            game_map = Map.objects.get(name=r.get('game_map'))

            submitter_user = User.objects.get(username=r.get('submitter'))
            ru, is_new_user = Rating_user.objects.get_or_create(
                user=submitter_user)

            g = Game.objects.create(
                start_date=r.get('start_date'),
                game_type=game_type,
                game_map=game_map,
                win_team=r.get('result'),
                submitter=ru,
                game_status=1,  # todo when working on user submissions
                game_breaks=0,  # todo when working on user submissions
            )
            g.save()

            for participant in p_data:
                user = User.objects.get(username=participant['user'])
                ru, is_new_user = Rating_user.objects.get_or_create(user=user)
                try:
                    u = User.objects.get(username=participant['user'])
                except:
                    return

                participant_tribe = Tribe.objects.get(
                    name=participant['tribe'])
                p = Participant.objects.create(
                    user=ru,
                    game=g,
                    team=participant['team'],
                    tribe=participant_tribe,
                )
                p.save()

        return render(request, 'wlrating/arbiter.html', {'game_list': get_arbiter_list()})


@login_required
def remove_btn(request, game_id):
    g = Game.objects.get(id=game_id)
    for p in Participant.objects.filter(game=g):
        p.delete()
    g.delete()

    return render(request, 'wlrating/arbiter.html', {'game_list': get_arbiter_list()})


@login_required
def calculate_scores(request):
    s, created = Season.objects.get_or_create(
        start_date='2019-06-01',
        end_date='2019-12-01',
        name='Season I: The season of many builds'
    )
    if created:
        s.save()

    for g in Game.objects.all():
        g.counted_in_score = False
        g.save()

    for pr in Player_Rating.objects.all():
        pr.delete()

    for ru in Rating_user.objects.all():
        nb_of_games = 0
        win = 0

        for p in Participant.objects.filter(user=ru):
            nb_of_games += 1
            g = Game.objects.get(id=p.game.id)
            win = win + 1 if g.win_team == p.team else win

        if nb_of_games > 0:
            try:
                pr = Player_Rating.objects.get(
                    user=ru,
                    rating_type=1,
                )
            except Player_Rating.DoesNotExist:
                pr = Player_Rating.objects.create(
                    user=ru,
                    rating_type=1,
                    decimal1=nb_of_games,
                    decimal2=win,
                    decimal3=Decimal(
                        win/nb_of_games).quantize(Decimal('1.00000')),
                    season=s,
                )
                pr.save()
            pr.decimal1 = nb_of_games
            pr.decimal2 = win
            pr.decimal3 = Decimal(win/nb_of_games).quantize(Decimal('1.00000'))
            pr.season = s
            pr.save()

    new_rating = Glicko_rating()
    new_rating.calculate_all_games('Season I: The season of many builds')

    return render(request, 'wlrating/arbiter.html', {'game_list': get_arbiter_list()})


@login_required
def add_test_data(request):
    create_test_data()
    return render(request, 'wlrating/arbiter.html', {'game_list': get_arbiter_list()})


def get_arbiter_list():
    game_list = []
    for g in Game.objects.order_by('start_date'):
        game_data = {}
        game_data['start_date'] = datetime.strftime(g.start_date, TIME_FORMAT)
        game_data['game_type'] = g.game_type.name
        game_data['game_map'] = g.game_map.name
        game_data['game_id'] = g.id

        players = []
        for p in Participant.objects.filter(game=g):
            player = {}
            player['tribe'] = p.tribe.name
            player['username'] = p.user.user.username
            player['team'] = p.team
            player['win_status'] = 'winner' if g.win_team == p.team else 'looser'
            players.append(player)

        game_data['players'] = players

        game_list.append(game_data)
    return game_list


@login_required
def score(request):
    win_ratio_board = []
    for pr in Player_Rating.objects.order_by('-decimal3').filter(rating_type=1):
        player_data = {}
        player_data['username'] = pr.user.user.username
        player_data['nb_of_games'] = int(pr.decimal1)
        player_data['win'] = int(pr.decimal2)
        player_data['win_ratio'] = int(pr.decimal3 * 100)
        win_ratio_board.append(player_data)

    glicko_board = []
    for pr in Player_Rating.objects.order_by('-decimal1').filter(rating_type=3):
        player_data = {}
        player_data['username'] = pr.user.user.username
        player_data['rating'] = int(pr.decimal1)
        player_data['deviation'] = int(pr.decimal2)
        player_data['volatility'] = int(pr.decimal3 * 100)
        glicko_board.append(player_data)

    return render(request, 'wlrating/score.html', {'win_ratio_board': win_ratio_board,
                                                   'glicko2_board': glicko_board})


# data html handling
def process_data_from_html(r):
    player_list = {}
    for dict_property, value in r.items():
        if value:
            if 'player' in dict_property:
                num = str(dict_property[-1])
                if not num in player_list:
                    player_list[num] = {}
                player_list[num]['player'] = value

            if 'tribe' in dict_property:
                num = str(dict_property[-1])
                if not num in player_list:
                    player_list[num] = {}
                player_list[num]['tribe'] = value

            if 'team' in dict_property:
                num = str(dict_property[-1])
                if not num in player_list:
                    player_list[num] = {}
                player_list[num]['team'] = value

    # Remove player which lack any property
    for p in list(player_list):
        if not 'player' in player_list[p] or not 'team' in player_list[p] or not 'tribe' in player_list[p]:
            del player_list[p]

    data = []
    for dict_property, player in player_list.items():
        participation = {}
        participation['user'] = player_list[dict_property]['player']
        participation['team'] = player_list[dict_property]['team']
        participation['tribe'] = player_list[dict_property]['tribe']
        data.append(participation)
    return data


# Utilities
def clean_list(l):
    for num, i in enumerate(l):
        if isinstance(i, str):
            l[num] = i.strip()

    return l


##########
## AJAX ##
##########
def get_ajax(request, model_to_get, property_to_get):
    """AJAX Callback for JS autocomplete.

    This is used for autocompletion of usernames when writing PMs.
    The path.name of this function has to be used in each place:
    1. Argument of source of the JS widget
    2. urls.py
    """
    if request.is_ajax():
        q = request.GET.get('term', '')
        contain_filter = property_to_get + '__contains'
        model_obj = model_to_get.objects.filter(**{contain_filter: q})
        results = []
        for o in model_obj:
            name_json = {'value': getattr(o, property_to_get)}
            results.append(name_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'

    return data, mimetype


def get_usernames(request):
    data, mimetype = get_ajax(request, User, 'username')
    return HttpResponse(data, mimetype)


def get_tribe(request):
    data, mimetype = get_ajax(request, Tribe, 'name')
    return HttpResponse(data, mimetype)


def get_map(request):
    data, mimetype = get_ajax(request, Map, 'name')
    return HttpResponse(data, mimetype)


def get_game_type(request):
    data, mimetype = get_ajax(request, GameType, 'name')
    return HttpResponse(data, mimetype)
