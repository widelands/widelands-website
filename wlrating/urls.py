#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from .view import rating_main, arbiter, score, remove_btn, calculate_scores, get_usernames, get_map, user_add_game

urlpatterns = [
    url(r'^$', rating_main, name='rating_main'),
    url(r'^arbiter/$', arbiter, name='arbiter'),
    url(r'^user_add_game/$', user_add_game, name='user_add_game'),
    url(r'^remove_btn/(?P<game_id>[0-9]+)$', remove_btn, name='remove_btn'),
    url(r'^calculate_scores/$', calculate_scores, name='calculate_scores'),
    url(r'^score/$', score, name='score'),
    url(r'^get_usernames/', get_usernames, name='get_usernames'),
    url(r'^get_map/', get_map, name='get_map'),
]
