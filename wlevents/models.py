#!/usr/bin/env python
# encoding: utf-8

import datetime

from django.db import models


class EventsManager(models.Manager):

    def open(self):
        return self.all().exclude(end_date__lt=datetime.datetime.now()).\
            order_by('end_date')


class Event(models.Model):
    name = models.CharField(max_length=256)
    link = models.CharField(max_length=1024)
    start_date = models.DateField('start date')
    end_date = models.DateField('end date', blank=True, null=True)

    objects = EventsManager()

    def in_the_past(self):
        return self.end_date < datetime.date.today()

    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.start_date

        return models.Model.save(self, *args, **kwargs)
