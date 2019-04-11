# -*- coding: utf-8 -*-


from django.db import models
from django.urls import reverse


class PrivacyPolicy(models.Model):

    language = models.CharField(default='English', max_length=30,
                                help_text='Will be displayed as a level 1 header',
                                unique=True)
    policy_text = models.TextField(
        help_text='Text will be rendered using markdown syntax')
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['language']

    def __str__(self):
        return self.language
    
    def get_absolute_url(self):
        return reverse('policy_translated', kwargs={'slug': self.slug})