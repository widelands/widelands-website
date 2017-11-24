from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
import re


class SuspiciousInput(models.Model):
    """Model for collecting suspicios user input.
    
    Call directly the send function with this attributes:
    content_object = Model instance of a saved(!) object
    user = user
    text = text to check for suspicious content
    
    Example:
    is_suspicous = SuspiciousInput(content_type=post, user=post.user, text=post.body).send()
    """
    
    text = models.CharField(max_length=200, verbose_name="suspicious user input")
    user = models.ForeignKey(User, verbose_name="related user")
    content_type = models.ForeignKey(ContentType, verbose_name="related model")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['content_type_id']
        default_permissions = ('change', 'delete',)

    def __unicode__(self):
        return self.text
    
    def is_suspicious(self):
        if any(x in self.text.lower() for x in settings.ANTI_SPAM_KWRDS):
            return True
        if re.search(settings.ANTI_SPAM_PHONE_NR, self.text):
            return True
        return False

    def save(self, *args, **kwargs):
        is_spam = self.is_suspicious()
        if is_spam:
            super(SuspiciousInput, self).save(*args, **kwargs)
        return is_spam
