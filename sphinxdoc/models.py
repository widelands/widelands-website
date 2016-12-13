# encoding: utf-8
"""
Models for django-sphinxdoc.
"""

from django.db import models


class App(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,
                            help_text=u'Used in the URL for the app. Must be unique.')
    path = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('doc-index', (), {'slug': self.slug})

    class Meta:
        app_label = 'sphinxdoc'
