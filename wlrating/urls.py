#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from .view import arbiter, score_1vs1, score_team, score_stats, remove_btn, calculate_scores, get_usernames, get_map, user_add_game

urlpatterns = [
    url(r'^$', score_1vs1, name='score_1vs1'),
    url(r'^score_team/$', score_team, name='score_team'),
    url(r'^score_stats/$', score_stats, name='score_stats'),
    url(r'^arbiter/$', arbiter, name='arbiter'),
    url(r'^user_add_game/$', user_add_game, name='user_add_game'),
    url(r'^remove_btn/(?P<game_id>[0-9]+)$', remove_btn, name='remove_btn'),
    url(r'^calculate_scores/$', calculate_scores, name='calculate_scores'),
    url(r'^get_usernames/', get_usernames, name='get_usernames'),
    url(r'^get_map/', get_map, name='get_map'),
]
