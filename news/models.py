from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User
from tagging.fields import TagField
from widelands.news.managers import PublicManager
from django.core.urlresolvers import reverse

from djangosphinx import SphinxSearch

import tagging


def get_upload_name( inst, fn ):
    try:
        extension = fn.split('.')[-1].lower()
    except:
        extension = 'png'
    return 'news/img/%s.%s' % (inst.title,extension)

class Category(models.Model):
    """Category model."""
    title       = models.CharField(_('title'), max_length=100)
    slug        = models.SlugField(_('slug'), unique=True)
    image       = models.ImageField( upload_to=get_upload_name, max_length=100 )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        db_table = 'news_categories'
        ordering = ('title',)

    class Admin:
        pass

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('news_category_detail', None, {'slug': self.slug})


class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
    )
    title           = models.CharField(_('title'), max_length=200)
    slug            = models.SlugField(_('slug'), unique_for_date='publish')
    author          = models.ForeignKey(User, blank=True, null=True)
    body            = models.TextField(_('body'))
    tease           = models.TextField(_('tease'), blank=True)
    status          = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    allow_comments  = models.BooleanField(_('allow comments'), default=True)
    publish         = models.DateTimeField(_('publish'))
    created         = models.DateTimeField(_('created'), auto_now_add=True)
    modified        = models.DateTimeField(_('modified'), auto_now=True)
    categories      = models.ManyToManyField(Category, blank=True)
    tags            = TagField()
    objects         = PublicManager()
    
    search          = SphinxSearch(
        weights = {
            'title': 100,
            'body': 80,
            'tease': 80,
            }
    )

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        db_table  = 'news_posts'
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    class Admin:
        list_display  = ('title', 'publish', 'status')
        list_filter   = ('publish', 'categories', 'status')
        search_fields = ('title', 'body')

    def __unicode__(self):
        return u'%s' % self.title
   
    #########
    # IMAGE #
    #########
    # Currently this is only inherited from the category, but one
    # day we might want to override the post image here
    @property
    def has_image(self):
        if self.categories.count() == 0:
            return False
        return self.categories.all()[0].image != ''
    @property
    def image(self):
        if self.categories.count() == 0:
            return None 
        return self.categories.all()[0].image
    @property
    def image_alt(self):
        "alt='' tag for <img>"
        if self.categories.count() == 0:
            return '' 
        return self.categories.all()[0].title

    @permalink
    def get_absolute_url(self):
        return ('news_detail', None, {
            'slug': self.slug,
            'year': self.publish.year,
            'month': self.publish.strftime('%m'),
            'day': self.publish.day,
        })
    
    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)
    
    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)

