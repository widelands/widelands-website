from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor
from django.db.models import OneToOneField
from django.db import models
import os
import shutil


def get_real_ip(request):
    """Returns the real user IP, even if behind a proxy."""
    for key in ("HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"):
        if key in request.META:
            return request.META[key]
    # No match -> Return a fictional IP to have the model fields not empty
    return "192.168.255.255"


# AutoOneToOneField
# =================
# This is used to create a wlprofile object for a user automatically:
# user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
# profile = user.wlprofile  -> Now the wlprofile is created
#
# Initial implemenation details about AutoOneToOneField:
#   http://softwaremaniacs.org/blog/2007/03/07/auto-one-to-one-field/
#
class AutoReverseOneToOneDescriptor(ReverseOneToOneDescriptor):
    """The descriptor that handles the object creation for an
    AutoOneToOneField."""

    def __get__(self, instance, instance_type=None):
        model = getattr(self.related, "related_model", self.related.model)

        try:
            return super(AutoReverseOneToOneDescriptor, self).__get__(
                instance, instance_type
            )
        except model.DoesNotExist:
            obj = model(**{self.related.field.name: instance})

            obj.save()

            # Don't return obj directly, otherwise it won't be added
            # to Django's cache, and the first 2 calls to obj.relobj
            # will return 2 different in-memory objects
            return super(AutoReverseOneToOneDescriptor, self).__get__(
                instance, instance_type
            )


class AutoOneToOneField(OneToOneField):
    """OneToOneField creates dependent object on first request from parent
    object if dependent object has not created yet."""

    def contribute_to_related_class(self, cls, related):
        setattr(
            cls, related.get_accessor_name(), AutoReverseOneToOneDescriptor(related)
        )


# Memory based cache does not allow whitespace or control characters in keys
# We are using a database cache atm, so this is just a forethought to
# prevent failures when switching to a memory based cache
def get_valid_cache_key(key):
    return key.replace(" ", "_")


def return_git_path(pgm="git"):
    """Find and return the path to git executable and check if it is valid."""
    git_path = shutil.which(pgm)
    if not git_path:
        git_path = "/usr/bin/git"
        if not os.path.exists(git_path) or not os.access(git_path, os.X_OK):
            return None
    return git_path
