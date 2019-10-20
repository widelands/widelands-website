#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Season(models.Model):
    start_date = models.DateTimeField()
    end_date= models.DateTimeField()
    name = models.CharField(max_length=255, blank=True, default='')

class Rating_user(models.Model):
    user = models.ForeignKey(User, related_name='user')

class Tribe(models.Model):
    name = models.CharField(max_length=255, default='')

class Map(models.Model):
    name = models.CharField(max_length=255, default='')

class GameType(models.Model):
    name = models.CharField(max_length=255, default='')

class Game(models.Model):
    GAME_STATUS = [(0, 'unfinished'), (1, 'winner_team'), (2, 'tie')]

    start_date = models.DateTimeField()
    game_type = models.ForeignKey(GameType, related_name='gametype')
    game_map = models.ForeignKey(Map, related_name='map')
    win_team = models.IntegerField()
    game_status = models.IntegerField(choices=GAME_STATUS)
    game_breaks = models.IntegerField()

    submitter = models.ForeignKey(Rating_user, related_name='+')
    counted_in_score = models.BooleanField(default=False)
    # here we can think about expanding to FK to uploaded maps too:
    # map_link = models.ForeignKey('?maps.map?', null=True, blank=True)
    # game_link

class Participant(models.Model):

    user = models.ForeignKey(Rating_user, related_name='+')
    game = models.ForeignKey(Game, related_name='participants')
    team = models.IntegerField()
    tribe = models.ForeignKey(Tribe, related_name='tribe')

class Player_Rating(models.Model):
    CHOICES_TYPE = [(1, 'simple'), (2, 'Elo'), (3, 'Glicko')]

    user = models.ForeignKey(Rating_user, related_name='+')
    rating_type = models.IntegerField(choices=CHOICES_TYPE )
    decimal1 = models.DecimalField(max_digits=15, decimal_places=10, default=0) # rating score for glicko
    decimal2 = models.DecimalField(max_digits=15, decimal_places=10, default=0) # rating_deviation for Glicko
    decimal3 = models.DecimalField(max_digits=15, decimal_places=10, default=0) # volatility for Glicko

    season = models.ForeignKey(Season, related_name='season')
