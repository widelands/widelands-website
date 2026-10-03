from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import GGZAuth


@receiver(post_save, sender=User, dispatch_uid="wlggz_delete_inactive_password")
def delete_password_of_inactive_user(sender, instance, **kwargs):
    """Inactive users (banned, locked, deleted) must not log in to the metaserver."""
    if not instance.is_active:
        GGZAuth.objects.filter(user=instance).delete()
