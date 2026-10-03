from django.db.models import signals
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _

from tagging import settings
from tagging.forms import TagField as TagFormField
from tagging.models import Tag
from tagging.utils import edit_string_for_tags


class TagField(CharField):
    """
    A "special" character field that actually works as a relationship to tags
    "under the hood". This exposes a space-separated string of tags, but does
    the splitting/reordering/etc. under the hood.
    """

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = kwargs.get("max_length", 255)
        kwargs["blank"] = kwargs.get("blank", True)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)

        # Make this object the descriptor for field access.
        setattr(cls, self.name, self)

        # Save tags back to the database post-save
        signals.post_save.connect(self._save, cls, True)

    def __get__(self, instance, owner=None):
        """Return the instance's tags as an editable string."""
        if instance is None:
            return self

        tags = self._get_instance_tag_cache(instance)
        if tags is None:
            if instance.pk is None:
                self._set_instance_tag_cache(instance, "")
            else:
                self._set_instance_tag_cache(
                    instance, edit_string_for_tags(Tag.objects.get_for_object(instance))
                )
        return self._get_instance_tag_cache(instance)

    def __set__(self, instance, value):
        """Set an object's tags."""
        if instance is None:
            raise AttributeError(_("%s can only be set on instances.") % self.name)
        if settings.FORCE_LOWERCASE_TAGS and value is not None:
            value = value.lower()
        self._set_instance_tag_cache(instance, value)

    def _save(self, **kwargs):
        """Save tags back to the database."""
        tags = self._get_instance_tag_cache(kwargs["instance"])
        if tags is not None:
            Tag.objects.update_tags(kwargs["instance"], tags)

    def __delete__(self, instance):
        """Clear all of an object's tags."""
        self._set_instance_tag_cache(instance, "")

    def _get_instance_tag_cache(self, instance):
        return getattr(instance, "_%s_cache" % self.attname, None)

    def _set_instance_tag_cache(self, instance, tags):
        # Writing to instance.__dict__ by-passes the deferred fields system
        # when saving an instance, which checks the keys present in
        # instance.__dict__.
        instance.__dict__[self.attname] = tags
        setattr(instance, "_%s_cache" % self.attname, tags)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {"form_class": TagFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
