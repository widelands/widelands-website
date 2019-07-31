#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    user = models.ForeignKey(User, related_name='game')
    start_date = models.DateTimeField(default=0)
    game_type = models.CharField(max_length=255)
    game_map = models.CharField(max_length=255)
    players = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    submitter = models.CharField(max_length=255)

class Rating(models.Model):
    player = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=10, decimal_places=2)
    standard_deviation = models.DecimalField(max_digits=10, decimal_places=2)
    volatility = models.DecimalField(max_digits=10, decimal_places=5)

