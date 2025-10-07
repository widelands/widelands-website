from datetime import datetime
from django.urls import reverse

# Google Diff Match Patch library
# http://code.google.com/p/google-diff-match-patch
from .diff_match_patch import diff_match_patch

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey

from tagging.fields import TagField

from wlimages.models import Image

try:
    from notification import models as notification
    from django.db.models import signals
except ImportError:
    notification = None

# We dont need to create a new one everytime
dmp = diff_match_patch()


def diff(txt1, txt2):
    """Create a 'diff' from txt1 to txt2."""
    patch = dmp.patch_make(txt1, txt2)
    return dmp.patch_toText(patch)


try:
    markup_choices = settings.WIKI_MARKUP_CHOICES
except AttributeError:
    markup_choices = (
        ("crl", _("Creole")),
        ("rst", _("reStructuredText")),
        ("txl", _("Textile")),
        ("mrk", _("Markdown")),
    )


class Article(models.Model):
    """A wiki page reflecting the actual revision."""

    title = models.CharField(_("Title"), max_length=50, unique=True)
    content = models.TextField(_("Content"))
    summary = models.CharField(_("Summary"), max_length=150, null=True, blank=True)
    markup = models.CharField(
        _("Content Markup"), max_length=3, choices=markup_choices, null=True, blank=True
    )
    creator = models.ForeignKey(
        User, verbose_name=_("Article Creator"), null=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(default=datetime.now)
    last_update = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(
        default=False,
        help_text="Check to mark as deleted",
    )

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True)
    group = GenericForeignKey("content_type", "object_id")

    images = GenericRelation(Image)

    tags = TagField()

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        app_label = "wiki"
        default_permissions = (
            "change",
            "add",
        )
        ordering = ["title"]

    def get_absolute_url(self):
        if self.group is None:
            return reverse("wiki_article", args=(self.title,))
        return self.group.get_absolute_url() + "wiki/" + self.title

    def save(self, *args, **kwargs):
        self.last_update = datetime.now()
        super(Article, self).save(*args, **kwargs)

    def latest_changeset(self):
        try:
            return self.changeset_set.filter(reverted=False).order_by("-revision")[0]
        except IndexError:
            return ChangeSet.objects.none()

    def all_images(self):
        return self.images.all()

    def new_revision(self, old_content, old_title, old_markup, comment, editor):
        """Create a new ChangeSet with the old content."""

        content_diff = diff(self.content, old_content)

        cs = ChangeSet.objects.create(
            article=self,
            comment=comment,
            editor=editor,
            old_title=old_title,
            old_markup=old_markup,
            content_diff=content_diff,
        )

        return cs

    def revert_to(self, revision, editor=None):
        """Revert the article to a previuos state, by revision number."""
        changeset = self.changeset_set.get(revision=revision)
        changeset.reapply(editor)

    def compare(self, from_revision, to_revision):
        """Compares to revisions of this article."""
        changeset = self.changeset_set.get(revision=to_revision)
        return changeset.compare_to(from_revision)

    def __str__(self):
        return self.title


class ChangeSetManager(models.Manager):
    def all_later(self, revision):
        """Return all changes later to the given revision.

        Util when we want to revert to the given revision.

        """
        return self.filter(revision__gt=int(revision))


class ChangeSetOfficial(models.Manager):
    def get_queryset(self):
        """Return a queryset which contains data for the public."""
        return super().get_queryset().exclude(article__deleted=True).exclude(editor=None)


class ChangeSet(models.Model):
    """A report of an older version of some Article."""

    article = models.ForeignKey(
        Article, verbose_name=_("Article"), on_delete=models.CASCADE
    )

    # Editor identification -- logged
    editor = models.ForeignKey(
        User, verbose_name=_("Editor"), null=True, on_delete=models.SET_NULL
    )

    # Revision number, starting from 1
    revision = models.IntegerField(_("Revision Number"))

    # How to recreate this version
    old_title = models.CharField(_("Old Title"), max_length=50, blank=True)
    old_markup = models.CharField(
        _("Article Content Markup"),
        max_length=3,
        choices=markup_choices,
        null=True,
        blank=True,
    )
    content_diff = models.TextField(_("Content Patch"), blank=True)

    comment = models.TextField(_("Editor comment"), blank=True)
    modified = models.DateTimeField(_("Modified at"), default=datetime.now)
    reverted = models.BooleanField(_("Reverted Revision"), default=False)

    objects = ChangeSetManager()
    official = ChangeSetOfficial()

    class Meta:
        verbose_name = _("Change set")
        verbose_name_plural = _("Change sets")
        get_latest_by = "modified"
        ordering = ("-revision",)
        app_label = "wiki"

    def __str__(self):
        return "#%s" % self.revision

    def get_absolute_url(self):
        if self.article.group is None:
            return reverse(
                "wiki_changeset",
                kwargs={"title": self.article.title, "revision": self.revision},
            )
        return reverse(
            "wiki_changeset",
            kwargs={
                "group_slug": self.article.group.slug,
                "title": self.article.title,
                "revision": self.revision,
            },
        )

    def is_anonymous_change(self):
        return self.editor is None

    def reapply(self, editor):
        """Return the Article to this revision."""

        # XXX Would be better to exclude reverted revisions
        #     and revisions previous/next to reverted ones
        next_changes = self.article.changeset_set.filter(
            revision__gt=self.revision
        ).order_by("-revision")

        article = self.article

        content = None
        for changeset in next_changes:
            if content is None:
                content = article.content
            patch = dmp.patch_fromText(changeset.content_diff)
            content = dmp.patch_apply(patch, content)[0]

            changeset.reverted = True
            changeset.save()

        old_content = article.content
        old_title = article.title
        old_markup = article.markup

        article.content = content
        article.title = changeset.old_title
        article.markup = changeset.old_markup
        article.save()

        article.new_revision(
            old_content=old_content,
            old_title=old_title,
            old_markup=old_markup,
            comment="Reverted to revision #%s" % self.revision,
            editor=editor,
        )

        self.save()

        if None not in (notification, self.editor):
            notification.send(
                [self.editor],
                "wiki_revision_reverted",
                {"revision": self, "article": self.article},
            )

    def save(self, *args, **kwargs):
        """Saves the article with a new revision."""
        if self.id is None:
            try:
                self.revision = (
                    ChangeSet.objects.filter(article=self.article).latest().revision + 1
                )
            except self.DoesNotExist:
                self.revision = 1

        super(ChangeSet, self).save(*args, **kwargs)

    def get_content(self):
        """Returns the content of this revision."""
        content = self.article.content
        newer_changesets = ChangeSet.objects.filter(
            article=self.article, revision__gt=self.revision
        ).order_by("-revision")
        for changeset in newer_changesets:
            patches = dmp.patch_fromText(changeset.content_diff)
            content = dmp.patch_apply(patches, content)[0]
        return content

    def compare_to(self, revision_from):
        other_content = ""
        if int(revision_from) > 0:
            other_content = (
                ChangeSet.objects.filter(
                    article=self.article, revision__lte=revision_from
                )
                .order_by("-revision")[0]
                .get_content()
            )
        diffs = dmp.diff_main(other_content, self.get_content())
        # dmp.diff_cleanupSemantic(diffs)
        return dmp.diff_prettyHtml(diffs)
