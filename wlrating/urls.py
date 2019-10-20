#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from .view import rating_main, arbiter, score, remove_btn, calculate_scores, add_test_data, get_usernames, get_tribe, get_map, get_game_type

urlpatterns = [
    url(r'^main/$', rating_main, name='rating_main'),
    url(r'^arbiter/$', arbiter, name='arbiter'),
    url(r'^remove_btn/(?P<game_id>[0-9]+)$', remove_btn, name='remove_btn'),
    url(r'^calculate_scores/$', calculate_scores, name='calculate_scores'),
    url(r'^add_test_data/$', add_test_data, name='add_test_data'),
    url(r'^score/$', score, name='score'),
    url(r'^get_usernames/', get_usernames, name="get_usernames"),
    url(r'^get_tribe/', get_tribe, name="get_tribe"),
    url(r'^get_map/', get_map, name="get_map"),
    url(r'^get_game_type/', get_game_type, name="get_game_type"),
]
