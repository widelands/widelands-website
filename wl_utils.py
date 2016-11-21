
# Make a save filename
VALID_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'wmf', 'wgf']
def make_safe_filename(name):
    
    name, sep, ext = name.rpartition('.')
    if not ext:
        # Each file must have an extension
        return None
    if not any(x in ext.lower() for x in VALID_EXTENSIONS):
        # No valid extension found
        return None

    filename = "".join([x if x.isalnum() else "_" for x in name]) + '.' + ext
    return filename

# Get the real IP when the Django server runs behind a proxy
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


# SingleRelatedObjectDescriptor gets renamed with Django 1.9
try:
    from django.db.models.fields.related import SingleRelatedObjectDescriptor
except ImportError:
    from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor as SingleRelatedObjectDescriptor

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
