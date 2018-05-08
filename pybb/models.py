from datetime import datetime
from mainpage.templatetags.wl_markdown import do_wl_markdown
import os.path
import hashlib

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from pybb.markups import mypostmarkup
from pybb.util import urlize, memoize_method, unescape
from pybb import settings as pybb_settings

from django.conf import settings
from notification.models import send
from django.contrib.auth.models import User

try:
    from notification import models as notification
    from django.db.models import signals
except ImportError:
    notification = None

MARKUP_CHOICES = (
    ('markdown', 'markdown'),
    ('bbcode', 'bbcode'),
)


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)

    class Meta:
        ordering = ['position']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return self.name

    def forum_count(self):
        return self.forums.all().count()

    def get_absolute_url(self):
        return reverse('pybb_category', args=[self.id])

    @property
    def topics(self):
        return Topic.objects.filter(forum__category=self).select_related()

    @property
    def posts(self):
        return Post.objects.filter(topic__forum__category=self).select_related()


class Forum(models.Model):
    category = models.ForeignKey(
        Category, related_name='forums', verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)
    description = models.TextField(_('Description'), blank=True, default='')
    moderators = models.ManyToManyField(
        User, blank=True, verbose_name=_('Moderators'))
    updated = models.DateTimeField(_('Updated'), null=True)

    class Meta:
        ordering = ['position']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __unicode__(self):
        return self.name

    def topic_count(self):
        return self.topics.all().count()

    def get_absolute_url(self):
        return reverse('pybb_forum', args=[self.id])

    @property
    def posts(self):
        return Post.objects.filter(topic__forum=self).exclude(hidden=True).select_related()

    @property
    def post_count(self):
        return Post.objects.filter(topic__forum=self).exclude(hidden=True).count()

    @property
    def last_post(self):
        posts = self.posts.exclude(hidden=True).order_by(
            '-created').select_related()
        try:
            return posts[0]
        except IndexError:
            return None


class Topic(models.Model):
    forum = models.ForeignKey(
        Forum, related_name='topics', verbose_name=_('Forum'))
    name = models.CharField(_('Subject'), max_length=255)
    created = models.DateTimeField(_('Created'), null=True)
    updated = models.DateTimeField(_('Updated'), null=True)
    user = models.ForeignKey(User, verbose_name=_('User'))
    views = models.IntegerField(_('Views count'), blank=True, default=0)
    sticky = models.BooleanField(_('Sticky'), blank=True, default=False)
    closed = models.BooleanField(_('Closed'), blank=True, default=False)
    subscribers = models.ManyToManyField(
        User, related_name='subscriptions', verbose_name=_('Subscribers'), blank=True)

    class Meta:
        ordering = ['-updated']
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    def __unicode__(self):
        return self.name

    @property
    def head(self):
        return self.posts.all().order_by('created').select_related()[0]

    @property
    def last_post(self):
        return self.posts.exclude(hidden=True).order_by('-created').select_related()[0]

    # If the first post of this topic is hidden, the topic is hidden
    @property
    def is_hidden(self):
        try:
            p = self.posts.order_by('created').filter(
                hidden=False).select_related()[0]
        except IndexError:
            return True
        return False

    @property
    def post_count(self):
        return Post.objects.filter(topic=self).exclude(hidden=True).count()

    def get_absolute_url(self):
        return reverse('pybb_topic', args=[self.id])

    def save(self, *args, **kwargs):
        new = self.id is None
        if new:
            self.created = datetime.now()
        super(Topic, self).save(*args, **kwargs)

    def update_read(self, user):
        read, new = Read.objects.get_or_create(user=user, topic=self)
        if not new:
            read.time = datetime.now()
            read.save()

    # def has_unreads(self, user):
        # try:
            #read = Read.objects.get(user=user, topic=self)
        # except Read.DoesNotExist:
            # return True
        # else:
            # return self.updated > read.time


class RenderableItem(models.Model):
    """Base class for models that has markup, body, body_text and body_html
    fields."""

    class Meta:
        abstract = True

    def render(self):
        if self.markup == 'bbcode':
            self.body_html = mypostmarkup.markup(self.body, auto_urls=False)
        elif self.markup == 'markdown':
            self.body_html = unicode(do_wl_markdown(
                self.body, 'bleachit'))
        else:
            raise Exception('Invalid markup property: %s' % self.markup)

        # Remove tags which was generated with the markup processor
        text = strip_tags(self.body_html)

        # Unescape entities which was generated with the markup processor
        self.body_text = unescape(text)

        self.body_html = urlize(self.body_html)


class Post(RenderableItem):
    topic = models.ForeignKey(
        Topic, related_name='posts', verbose_name=_('Topic'))
    user = models.ForeignKey(
        User, related_name='posts', verbose_name=_('User'))
    created = models.DateTimeField(_('Created'), blank=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    markup = models.CharField(_('Markup'), max_length=15,
                              default=pybb_settings.DEFAULT_MARKUP, choices=MARKUP_CHOICES)
    body = models.TextField(_('Message'))
    body_html = models.TextField(_('HTML version'))
    body_text = models.TextField(_('Text version'))
    user_ip = models.GenericIPAddressField(_('User IP'), default='')
    hidden = models.BooleanField(_('Hidden'), blank=True, default=False)

    class Meta:
        ordering = ['created']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def summary(self):
        LIMIT = 50
        tail = len(self.body) > LIMIT and '...' or ''
        return self.body[:LIMIT] + tail

    __unicode__ = summary

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = datetime.now()

        self.render()

        new = self.id is None

        if new:
            self.topic.updated = datetime.now()
            self.topic.save()
            self.topic.forum.updated = self.topic.updated
            self.topic.forum.save()

        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pybb_post', args=[self.id])

    def unhide_post(self):
        """Unhide post(s) and inform subscribers."""
        self.hidden = False
        self.save()
        if self.topic.post_count == 1:
            # The topic is new
            send(User.objects.all(), 'forum_new_topic',
                 {'topic': self.topic, 'post': self, 'user': self.topic.user})
        else:
            # Inform topic subscribers
            send(self.topic.subscribers.all(), 'forum_new_post',
                 {'post': self, 'topic': self.topic, 'user': self.user})

    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by('created')[0].id
        super(Post, self).delete(*args, **kwargs)

        self.topic.save()
        self.topic.forum.save()

        if self_id == head_post_id:
            self.topic.delete()


class Read(models.Model):
    """For each topic that user has entered the time is logged to this
    model."""

    user = models.ForeignKey(User, verbose_name=_('User'))
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'))
    time = models.DateTimeField(_('Time'), blank=True)

    class Meta:
        unique_together = ['user', 'topic']
        verbose_name = _('Read')
        verbose_name_plural = _('Reads')

    def save(self, *args, **kwargs):
        if self.time is None:
            self.time = datetime.now()
        super(Read, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'T[%d], U[%d]: %s' % (self.topic.id, self.user.id, unicode(self.time))


class PrivateMessage(RenderableItem):

    dst_user = models.ForeignKey(User, verbose_name=_(
        'Recipient'), related_name='dst_users')
    src_user = models.ForeignKey(User, verbose_name=_(
        'Author'), related_name='src_users')
    read = models.BooleanField(_('Read'), blank=True, default=False)
    created = models.DateTimeField(_('Created'), blank=True)
    markup = models.CharField(_('Markup'), max_length=15,
                              default=pybb_settings.DEFAULT_MARKUP, choices=MARKUP_CHOICES)
    subject = models.CharField(_('Subject'), max_length=255)
    body = models.TextField(_('Message'))
    body_html = models.TextField(_('HTML version'))
    body_text = models.TextField(_('Text version'))

    class Meta:
        ordering = ['-created']
        verbose_name = _('Private message')
        verbose_name_plural = _('Private messages')

    # TODO: summary and part of the save method is the same as in the Post model
    # move to common functions
    def summary(self):
        LIMIT = 50
        tail = len(self.body) > LIMIT and '...' or ''
        return self.body[:LIMIT] + tail

    def __unicode__(self):
        return self.subject

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = datetime.now()
        self.render()

        new = self.id is None
        super(PrivateMessage, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pybb_show_pm', args=[self.id])


class Attachment(models.Model):
    post = models.ForeignKey(Post, verbose_name=_(
        'Post'), related_name='attachments')
    size = models.IntegerField(_('Size'))
    content_type = models.CharField(_('Content type'), max_length=255)
    path = models.CharField(_('Path'), max_length=255)
    name = models.TextField(_('Name'))
    hash = models.CharField(_('Hash'), max_length=40,
                            blank=True, default='', db_index=True)

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = hashlib.sha1(
                str(self.id) + settings.SECRET_KEY).hexdigest()
        super(Attachment, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pybb_attachment', args=[self.hash])

    def size_display(self):
        size = self.size
        if size < 1024:
            return '%b' % size
        elif size < 1024 * 1024:
            return '%dKb' % int(size / 1024)
        else:
            return '%.2fMb' % (size / float(1024 * 1024))

    def get_absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, pybb_settings.ATTACHMENT_UPLOAD_TO,
                            self.path)


if notification is not None:
    signals.post_save.connect(notification.handle_observations, sender=Post)

from pybb import signals
signals.setup_signals()
