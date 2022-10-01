from datetime import datetime
from mainpage.templatetags.wl_markdown import do_wl_markdown
import os.path
import hashlib

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from pybb.markups import mypostmarkup
from pybb.util import urlize, unescape
from pybb import settings as pybb_settings

from django.conf import settings
from notification.models import send
from check_input.models import SuspiciousInput
import magic

try:
    from notification import models as notification
    from django.db.models import signals
except ImportError:
    notification = None

MARKUP_CHOICES = (
    ("markdown", "markdown"),
    ("bbcode", "bbcode"),
)


class PybbExcludeInternal(models.Manager):
    def get_queryset(self):
        return super(PybbExcludeInternal, self).get_queryset().exclude(internal=True)


class Category(models.Model):
    """The base model of pybb.

    If 'internal' is set to True, the category is only visible for superusers and
    users which have the permission 'can_access_internal'.
    """

    name = models.CharField(_("Name"), max_length=80)
    position = models.IntegerField(_("Position"), blank=True, default=0)
    internal = models.BooleanField(
        default=False,
        verbose_name=_("Internal Category"),
        help_text=_("If set, this category is only visible for special users."),
    )

    objects = models.Manager()
    exclude_internal = PybbExcludeInternal()

    class Meta:
        ordering = ["position"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        # See also settings.INTERNAL_PERM
        permissions = (("can_access_internal", "Can access Internal Forums"),)

    def __str__(self):
        return self.name

    def forum_count(self):
        return self.forums.all().count()

    def get_absolute_url(self):
        return reverse("pybb_category", args=[self.id])

    @property
    def topics(self):
        return Topic.objects.filter(forum__category=self).select_related()

    @property
    def posts(self):
        return Post.objects.filter(topic__forum__category=self).select_related()


class Forum(models.Model):
    category = models.ForeignKey(
        Category, related_name="forums", verbose_name=_("Category")
    )
    name = models.CharField(_("Name"), max_length=80)
    position = models.IntegerField(_("Position"), blank=True, default=0)
    description = models.TextField(_("Description"), blank=True, default="")
    updated = models.DateTimeField(_("Updated"), null=True)
    moderator_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
        help_text="Users in this Group will have administrative permissions in this Forum.",
    )

    class Meta:
        ordering = ["position"]
        verbose_name = _("Forum")
        verbose_name_plural = _("Forums")

    def __str__(self):
        return self.name

    def topic_count(self):
        return self.topics.all().count()

    def get_absolute_url(self):
        return reverse("pybb_forum", args=[self.id])

    @property
    def posts(self):
        return (
            Post.objects.filter(topic__forum=self).exclude(hidden=True).select_related()
        )

    @property
    def post_count(self):
        return Post.objects.filter(topic__forum=self).exclude(hidden=True).count()

    @property
    def last_post(self):
        # This has better performance than using the posts manager hidden_topics
        # We search only for the last 10 topics
        topics = self.topics.order_by("-updated")[:10]
        posts = []
        for topic in topics:
            if topic.is_hidden:
                continue
            posts = (
                topic.posts.exclude(hidden=True).order_by("-created").select_related()
            )
            break

        try:
            return posts[0]
        except IndexError:
            return None


class Topic(models.Model):
    forum = models.ForeignKey(Forum, related_name="topics", verbose_name=_("Forum"))
    name = models.CharField(_("Subject"), max_length=255)
    created = models.DateTimeField(_("Created"), null=True)
    updated = models.DateTimeField(_("Updated"), null=True)
    user = models.ForeignKey(User, verbose_name=_("User"))
    views = models.IntegerField(_("Views count"), blank=True, default=0)
    sticky = models.BooleanField(_("Sticky"), blank=True, default=False)
    closed = models.BooleanField(_("Closed"), blank=True, default=False)
    subscribers = models.ManyToManyField(
        User, related_name="subscriptions", verbose_name=_("Subscribers"), blank=True
    )

    class Meta:
        ordering = ["-updated"]
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    def __str__(self):
        return self.name

    @property
    def head(self):
        try:
            return self.posts.all().order_by("created").select_related()[0]
        except:
            return None

    @property
    def last_post(self):
        return self.posts.exclude(hidden=True).order_by("-created").select_related()[0]

    @property
    def is_hidden(self):
        # If the first post of this topic is hidden, the topic is hidden
        try:
            return self.posts.first().hidden
        except:
            return False

    @property
    def post_count(self):
        return Post.objects.filter(topic=self).exclude(hidden=True).count()

    def get_absolute_url(self):
        return reverse("pybb_topic", args=[self.id])

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
    # read = Read.objects.get(user=user, topic=self)
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
        if self.markup == "bbcode":
            self.body_html = mypostmarkup.markup(self.body, auto_urls=False)
        elif self.markup == "markdown":
            self.body_html = str(do_wl_markdown(self.body, "bleachit"))
        else:
            raise Exception("Invalid markup property: %s" % self.markup)

        # Remove tags which was generated with the markup processor
        text = strip_tags(self.body_html)

        # Unescape entities which was generated with the markup processor
        self.body_text = unescape(text)

        self.body_html = urlize(self.body_html)


class HiddenTopicsManager(models.Manager):
    """Find all hidden topics by posts.

    A whole topic is hidden, if the first post is hidden.
    This manager returns the hidden topics and can be used to filter them out
    like so:

    Post.objects.exclude(topic__in=Post.hidden_topics.all()).filter(...)

    Use this with caution, because it affects performance, see:
    https://docs.djangoproject.com/en/dev/ref/models/querysets/#in
    """

    def get_queryset(self, *args, **kwargs):
        qs = super(HiddenTopicsManager, self).get_queryset().filter(hidden=True)

        hidden_topics = []
        try:
            for post in qs:
                if post.topic.is_hidden:
                    hidden_topics.append(post.topic)
            return hidden_topics
        except:
            return []


class PublicPostsManager(models.Manager):
    def public(self, limit=None, date_from=None):
        """Get public posts.

        Filters out all posts which shouldn't be visible to
        normal visitors. The result is always orderd by the
        posts creation time, Descending. Optional arguments:

        limit:     Slice the QuerySet [:limit].
        date_from: Gathers all posts from this day until today.
        """

        qs = (
            self.get_queryset()
            .filter(topic__forum__category__internal=False, hidden=False)
            .exclude(topic__in=Post.hidden_topics.all())
            .order_by("-created")
        )

        if date_from:
            qs = qs.filter(created__gte=date_from)
        if limit:
            qs = qs[:limit]

        return qs


class Post(RenderableItem):
    topic = models.ForeignKey(Topic, related_name="posts", verbose_name=_("Topic"))
    user = models.ForeignKey(User, related_name="posts", verbose_name=_("User"))
    created = models.DateTimeField(_("Created"), blank=True)
    updated = models.DateTimeField(_("Updated"), blank=True, null=True)
    markup = models.CharField(
        _("Markup"),
        max_length=15,
        default=pybb_settings.DEFAULT_MARKUP,
        choices=MARKUP_CHOICES,
    )
    body = models.TextField(_("Message"))
    body_html = models.TextField(_("HTML version"))
    body_text = models.TextField(_("Text version"))
    hidden = models.BooleanField(_("Hidden"), blank=True, default=False)

    objects = PublicPostsManager()  # Normal manager, extended
    hidden_topics = HiddenTopicsManager()  # Custom manager

    class Meta:
        ordering = ["created"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def summary(self):
        LIMIT = 50
        tail = len(self.body) > LIMIT and "..." or ""
        return self.body[:LIMIT] + tail

    __str__ = summary

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
        return reverse("pybb_post", args=[self.id])

    def unhide_post(self):
        """Unhide post(s) and inform subscribers."""
        self.hidden = False
        self.save()
        if self.topic.post_count == 1:
            # The topic is new
            send(
                User.objects.all(),
                "forum_new_topic",
                {"topic": self.topic, "post": self, "user": self.topic.user},
            )
        else:
            # Inform topic subscribers
            send(
                self.topic.subscribers.all(),
                "forum_new_post",
                {"post": self, "topic": self.topic, "user": self.user},
            )

    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by("created")[0].id

        if self.attachments.all():
            for attach in self.attachments.all():
                attach.delete()

        super(Post, self).delete(*args, **kwargs)

        self.topic.save()
        self.topic.forum.save()

        if self_id == head_post_id:
            self.topic.delete()

    def is_spam(self):
        try:
            SuspiciousInput.objects.get(object_id=self.pk)
            return True
        except:
            pass
        return False


class Read(models.Model):
    """For each topic that user has entered the time is logged to this
    model."""

    user = models.ForeignKey(User, verbose_name=_("User"))
    topic = models.ForeignKey(Topic, verbose_name=_("Topic"))
    time = models.DateTimeField(_("Time"), blank=True)

    class Meta:
        unique_together = ["user", "topic"]
        verbose_name = _("Read")
        verbose_name_plural = _("Reads")

    def save(self, *args, **kwargs):
        if self.time is None:
            self.time = datetime.now()
        super(Read, self).save(*args, **kwargs)

    def __str__(self):
        return "T[%d], U[%d]: %s" % (self.topic.id, self.user.id, str(self.time))


class Attachment(models.Model):
    post = models.ForeignKey(Post, verbose_name=_("Post"), related_name="attachments")
    size = models.IntegerField(_("Size"))
    content_type = models.CharField(_("Content type"), max_length=255)
    path = models.CharField(_("Path"), max_length=255)
    name = models.TextField(_("Name"))
    hash = models.CharField(
        _("Hash"), max_length=40, blank=True, default="", db_index=True
    )

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = hashlib.sha1(
                bytes(self.id) + settings.SECRET_KEY.encode("utf-8")
            ).hexdigest()
        super(Attachment, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pybb_attachment", args=[self.hash])

    def get_absolute_path(self):
        return os.path.join(
            settings.MEDIA_ROOT, pybb_settings.ATTACHMENT_UPLOAD_TO, self.path
        )

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.get_absolute_path())
        except FileNotFoundError:
            pass
        super(Attachment, self).delete(*args, **kwargs)


if notification is not None:
    signals.post_save.connect(notification.handle_observations, sender=Post)

from pybb import signals

signals.setup_signals()
