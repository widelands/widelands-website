#!/usr/bin/env python -tt
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import datetime
try:
    from notification import models as notification
except ImportError:
    notification = None

import settings
if settings.USE_SPHINX:
    from djangosphinx.models import SphinxSearch

from djangoratings.fields import AnonymousRatingField


class Map(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=255)
    w = models.PositiveIntegerField(verbose_name='Width')
    h = models.PositiveIntegerField(verbose_name='Height')
    nr_players = models.PositiveIntegerField(verbose_name='Max Players')

    descr = models.TextField(verbose_name='Description')
    hint = models.TextField(verbose_name='Hint')
    minimap = models.ImageField(
        verbose_name='Minimap', upload_to='wlmaps/minimaps')
    file = models.FileField(verbose_name='Mapfile',
                            upload_to='wlmaps/maps')

    world_name = models.CharField(max_length=50)

    pub_date = models.DateTimeField(default=datetime.datetime.now)
    uploader_comment = models.TextField(
        verbose_name='Uploader comment', blank=True)
    uploader = models.ForeignKey(User)
    nr_downloads = models.PositiveIntegerField(
        verbose_name='Download count', default=0)

    rating = AnonymousRatingField(range=10, can_change_vote=True)

    if settings.USE_SPHINX:
        search = SphinxSearch(
            weights={
                'name': 100,
                'author': 60,
                'uploader_comment': 40,
            }
        )

    class Meta:
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    @models.permalink
    def get_absolute_url(self):
        return ('wlmaps_view', None, {'map_slug': self.slug})

    def __unicode__(self):
        return u'%s by %s' % (self.name, self.author)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        map = super(Map, self).save(*args, **kwargs)
        if notification:
            notification.send(notification.get_observers_for('maps_new_map'), 'maps_new_map',
                              {'mapname': self.name, 'url': self.get_absolute_url(), 'user': self.uploader, 'uploader_comment': self.uploader_comment}, queue=True)

        return map    
