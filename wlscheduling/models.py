#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Availabilities(models.Model):
    user = models.ForeignKey(User, related_name='availabilities')
    avail_time = models.DateTimeField(
        ('one hour of availability'), default=0)