from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from news.managers import PublicManager
from django.urls import reverse
import datetime


def get_upload_name(inst, fn):
    try:
        extension = fn.split(".")[-1].lower()
    except:
        extension = "png"
    return "news/img/%s.%s" % (inst.title, extension)


class Category(models.Model):
    """Category model."""

    title = models.CharField(_("title"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    image = models.ImageField(upload_to=get_upload_name, max_length=100)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        db_table = "news_categories"
        ordering = ("title",)

    def __str__(self):
        return "%s" % self.title

    def get_absolute_url(self):
        return reverse("category_posts", args=(self.slug,))


class Post(models.Model):
    """Post model."""

    STATUS_CHOICES = (
        (1, _("Draft")),
        (2, _("Public")),
    )
    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), unique_for_date="publish")
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    body = models.TextField(
        _("body"), help_text="Text entered here will be rendered using Markdown"
    )
    tease = models.TextField(_("tease"), blank=True)
    status = models.IntegerField(_("status"), choices=STATUS_CHOICES, default=2)
    allow_comments = models.BooleanField(_("allow comments"), default=True)
    publish = models.DateTimeField(_("publish"))
    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)
    categories = models.ManyToManyField(Category, blank=True)

    objects = PublicManager()

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        db_table = "news_posts"
        ordering = ("-publish",)
        get_latest_by = "publish"

    def __str__(self):
        return "%s" % self.title

    #########
    # IMAGE #
    #########
    # Currently this is only inherited from the category, but one
    # day we might want to override the post image here
    @property
    def has_image(self):
        if self.categories.count() == 0:
            return False
        return self.categories.all()[0].image != ""

    @property
    def image(self):
        if self.categories.count() == 0:
            return None
        return self.categories.all()[0].image

    @property
    def image_alt(self):
        "alt='' tag for <img>"
        if self.categories.count() == 0:
            return ""
        return self.categories.all()[0].title

    def get_absolute_url(self):
        return reverse(
            "news_detail",
            args=(
                self.publish.year,
                self.publish.strftime("%b"),
                self.publish.day,
                self.slug,
            ),
        )

    def get_category_slug(self):
        try:
            s = self.categories.all()[0].slug
        except IndexError:
            return "none"
        return s

    def get_previous_post(self):
        # get_previous_by_FOO(**kwargs) is a django model function
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        # get_next_by_FOO(**kwargs) is a django model function
        return self.get_next_by_publish(
            status__gte=2, publish__lte=datetime.datetime.now()
        )
