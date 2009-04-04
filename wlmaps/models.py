#!/usr/bin/env python -tt
# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import datetime

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
    
    descr = models.TextField( verbose_name = "Description" )
    minimap = models.ImageField( upload_to ="/wlmaps/minimaps/" )
    
    world_name = models.CharField( max_length = 50  )

    pub_date = models.DateField( default = datetime.datetime.now )
    uploader_comment = models.TextField( )
    uploader = models.ForeignKey(User)
    nr_downloads = models.PositiveIntegerField( verbose_name ="Download count", default = 0)
    
    objects = MapManager()
    
    @models.permalink
    def get_absolute_url( self ):
        return ("wlmaps_view", None, {"map_slug": self.slug } )

    def __unicode__(self):
        return u'%s by %s' % (self.name, self.author)
