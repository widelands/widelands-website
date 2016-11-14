
def get_real_ip(request):
    """Returns the real user IP, even if behind a proxy."""
    for key in ('HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'):
        if key in request.META:
            return request.META[key]
    # No match -> Return a fictional IP to have the model fields not empty
    return '192.168.255.255'


# AutoOneToOneField
# =================
# Initial implemenation details about AutoOneToOneField:
#   http://softwaremaniacs.org/blog/2007/03/07/auto-one-to-one-field/
#
# This doesn't worked anymore with django 1.8
# changed according to:
#   https://github.com/skorokithakis/django-annoying/issues/36
#
# Needs also changes in Django 1.9 because of renaming:
# https://docs.djangoproject.com/en/1.9/releases/1.9/#miscellaneous
#   SingleRelatedObjectDescriptor is ReverseOneToOneDescriptor

from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db import models

class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    """
    The descriptor that handles the object creation for an AutoOneToOneField.
    """
    def __get__(self, instance, instance_type=None):
        model = getattr(self.related, 'related_model', self.related.model)

        try:
            return (super(AutoSingleRelatedObjectDescriptor, self)
                    .__get__(instance, instance_type))
        except model.DoesNotExist:
            obj = model(**{self.related.field.name: instance})

            obj.save()

            # Don't return obj directly, otherwise it won't be added
            # to Django's cache, and the first 2 calls to obj.relobj
            # will return 2 different in-memory objects
            return (super(AutoSingleRelatedObjectDescriptor, self)
                    .__get__(instance, instance_type))

class AutoOneToOneField(OneToOneField):
    """
    OneToOneField creates dependent object on first request from parent object
    if dependent oject has not created yet.
    """

    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))
        #if not cls._meta.one_to_one_field:
            #cls._meta.one_to_one_field = self