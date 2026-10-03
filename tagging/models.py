from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from tagging import settings
from tagging.utils import parse_tag_input


class TagManager(models.Manager):
    def update_tags(self, obj, tag_names):
        """Update tags associated with an object."""
        ctype = ContentType.objects.get_for_model(obj)
        current_tags = list(
            self.filter(items__content_type__pk=ctype.pk, items__object_id=obj.pk)
        )
        updated_tag_names = parse_tag_input(tag_names)
        if settings.FORCE_LOWERCASE_TAGS:
            updated_tag_names = [t.lower() for t in updated_tag_names]

        # Remove tags which no longer apply
        tags_for_removal = [
            tag for tag in current_tags if tag.name not in updated_tag_names
        ]
        if tags_for_removal:
            TaggedItem._default_manager.filter(
                content_type__pk=ctype.pk,
                object_id=obj.pk,
                tag__in=tags_for_removal,
            ).delete()
        # Add new tags
        current_tag_names = [tag.name for tag in current_tags]
        for tag_name in updated_tag_names:
            if tag_name not in current_tag_names:
                tag, created = self.get_or_create(name=tag_name)
                TaggedItem._default_manager.get_or_create(
                    content_type_id=ctype.pk,
                    object_id=obj.pk,
                    tag=tag,
                )

    def get_for_object(self, obj):
        """Return a queryset of all tags associated with the given object."""
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(items__content_type__pk=ctype.pk, items__object_id=obj.pk)


class Tag(models.Model):
    name = models.CharField(
        _("name"), max_length=settings.MAX_TAG_LENGTH, unique=True, db_index=True
    )

    objects = TagManager()

    class Meta:
        ordering = ("name",)
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name


class TaggedItem(models.Model):
    """Holds the relationship between a tag and the item being tagged."""

    tag = models.ForeignKey(
        Tag, verbose_name=_("tag"), related_name="items", on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(
        ContentType, verbose_name=_("content type"), on_delete=models.CASCADE
    )

    object_id = models.PositiveIntegerField(_("object id"), db_index=True)

    object = GenericForeignKey("content_type", "object_id")

    class Meta:
        # Enforce unique tag association per object
        unique_together = (("tag", "content_type", "object_id"),)
        verbose_name = _("tagged item")
        verbose_name_plural = _("tagged items")

    def __str__(self):
        return "%s [%s]" % (smart_str(self.object), smart_str(self.tag))
