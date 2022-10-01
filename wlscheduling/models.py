#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Availabilities(models.Model):
    user = models.ForeignKey(User, related_name='availabilities', on_delete=models.CASCADE)
    avail_time = models.DateTimeField(
        help_text="this user is available for this whole hour", default=0)
