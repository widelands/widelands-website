#!/usr/bin/env python -tt
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db.models.signals import pre_delete
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating

import datetime
import os
try:
    from notification import models as notification
except ImportError:
    notification = None


class Map(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=255)
    w = models.PositiveIntegerField(verbose_name='Width')
    h = models.PositiveIntegerField(verbose_name='Height')
    nr_players = models.PositiveIntegerField(verbose_name='Max Players')

    descr = models.TextField(verbose_name='Description')
    hint = models.TextField(verbose_name='Hint', blank=True)
    minimap = models.ImageField(
        verbose_name='Minimap', upload_to='wlmaps/minimaps')
    file = models.FileField(verbose_name='Mapfile',
                            upload_to='wlmaps/maps')

    world_name = models.CharField(max_length=50, blank=True)

    pub_date = models.DateTimeField(default=datetime.datetime.now)
    uploader_comment = models.TextField(
        verbose_name='Uploader comment', blank=True)
    uploader = models.ForeignKey(User)
    nr_downloads = models.PositiveIntegerField(
        verbose_name='Download count', default=0)
    wl_version_after = models.PositiveIntegerField(
        verbose_name='WL version after',
        null=True,
        blank=True)
    ratings = GenericRelation(Rating)

    class Meta:
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def get_absolute_url(self):
        return reverse('wlmaps_view', kwargs={'map_slug': self.slug})

    def __str__(self):
        return '%s by %s' % (self.name, self.author)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Check if this is a new map for sending notifications
        is_new = False
        try:
            Map.objects.get(slug=self.slug)
        except Map.DoesNotExist:
            is_new = True

        map = super(Map, self).save(*args, **kwargs)

        # Send notifications only on new maps, not when updating fields, e.g.
        # nr_downloads
        if notification and is_new:
            notification.send(notification.get_observers_for('maps_new_map', excl_user=self.uploader), 'maps_new_map',
                              {'mapname': self.name,
                               'url': self.get_absolute_url(),
                               'user': self.uploader,
                               'uploader_comment': self.uploader_comment
                               },
                              )

        return map

    def delete(self, *args, **kwargs):
        """Delete also corresponding map files."""

        # For some reason this throws no error if a file didn't exist
        self.minimap.delete()
        self.file.delete()
        super(Map, self).delete(*args, **kwargs)
