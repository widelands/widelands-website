#!/usr/bin/env python -tt
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import datetime

import settings
if settings.USE_SPHINX:
    from djangosphinx.models import SphinxSearch

from djangoratings.fields import AnonymousRatingField

class MapManager(models.Manager):
    def create(self,**kwargs):
        if 'slug' not in kwargs:
            name = kwargs['name']
            slug = slugify(name)
            m = super(MapManager,self).create(slug=slug, **kwargs)
        else:
            m = super(MapManager,self).create(**kwargs)

        return m


class Map(models.Model):
    name = models.CharField( max_length = 255, unique = True )
    slug = models.SlugField(unique=True)
    author = models.CharField( max_length = 255 )
    w = models.PositiveIntegerField( verbose_name = 'Width')
    h = models.PositiveIntegerField( verbose_name = 'Height')
    nr_players = models.PositiveIntegerField( verbose_name = 'Max Players')

    descr = models.TextField( verbose_name = "Description" )
    minimap = models.ImageField( upload_to ="/wlmaps/minimaps/" )
    file = models.FileField( upload_to ="/wlmaps/maps/" )

    world_name = models.CharField( max_length = 50  )

    pub_date = models.DateTimeField( default = datetime.datetime.now )
    uploader_comment = models.TextField( )
    uploader = models.ForeignKey(User)
    nr_downloads = models.PositiveIntegerField( verbose_name ="Download count", default = 0)

    rating = AnonymousRatingField(range=10, can_change_vote = True)

    if settings.USE_SPHINX:
        search          = SphinxSearch(
            weights = {
                'name': 100,
                'author': 60,
                }
        )

    class Meta:
        ordering  = ('-pub_date',)
        get_latest_by = 'pub_date'

    objects = MapManager()

    @models.permalink
    def get_absolute_url( self ):
        return ("wlmaps_view", None, {"map_slug": self.slug } )

    def __unicode__(self):
        return u'%s by %s' % (self.name, self.author)
