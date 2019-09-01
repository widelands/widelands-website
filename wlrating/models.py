#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Season(models.Model):
    start_date = models.DateTimeField()
    end_date= models.DateTimeField()
    name = models.CharField(max_length=255, blank=True, default='')

    
class Temporary_user(models.Model):
    username = models.CharField(max_length=255, blank=True, default='')


class Game(models.Model):

    CHOICES_GAME_TYPE = ((1, 'Autocrat'), (2, 'Wood gnome'))
    GAME_STATUS = [('0', 'unfinished'), ('1', 'winner_team'), ('2', 'tie')]

    start_date = models.DateTimeField()
    game_type = models.IntegerField(choices=CHOICES_GAME_TYPE)
    game_map = models.CharField(max_length=255, default='')
    win_team = models.IntegerField()
    game_status = models.IntegerField(choices=GAME_STATUS)
    game_breaks = models.IntegerField()
    # here we can think about expanding to FK to uploaded maps too:
    # map_link = models.ForeignKey('?maps.map?', null=True, blank=True)
    # game_link

class Participant(models.Model):
    TRIBE_TYPE = [('1', 'empire'), ('2', 'barbarian'), ('3', 'atlantean'), ('4', 'frisian')]

    user = models.ForeignKey(Temporary_user, related_name='user')
    game = models.ForeignKey(Game, related_name='participants')
    team = models.IntegerField()
    submitter = models.BooleanField(default=False)
    tribe = models.IntegerField(choices=TRIBE_TYPE)

class Player_Rating(models.Model):
    CHOICES_TYPE = [('1', 'simple'), ('2', 'Elo'), ('3', 'Glicko')]

    user = models.ForeignKey(Temporary_user, related_name='temp_user')
    rating_type = models.IntegerField(choices=CHOICES_TYPE )
    decimal1 = models.DecimalField(max_digits=10, decimal_places=5, default=0) # rating score for glicko
    decimal2 = models.DecimalField(max_digits=10, decimal_places=5, default=0) # rating_deviation for Glicko
    decimal3 = models.DecimalField(max_digits=10, decimal_places=5, default=0) # volatility for Glicko

    season = models.ForeignKey(Season, related_name='season')
