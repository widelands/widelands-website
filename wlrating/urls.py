#!/usr/bin/env python -tt
# encoding: utf-8
from django.conf.urls import *
from .view import rating_main, arbiter, score, remove_btn, calculate_scores, add_test_data

urlpatterns = [
    url(r'^main/$', rating_main, name='rating_main'),
    url(r'^arbiter/$', arbiter, name='arbiter'),
    url(r'^remove_btn/(?P<game_id>[0-9]+)$', remove_btn, name='remove_btn'),
    url(r'^calculate_scores/$', calculate_scores, name='calculate_scores'),
    url(r'^add_test_data/$', add_test_data, name='add_test_data'),
    url(r'^score/$', score, name='score'),
]
