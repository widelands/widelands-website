from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
import re


class SuspiciousInput(models.Model):
    """Model for collecting suspicios user input.

        Call the check_input method with this attributes:
        content_object = Model instance of a saved(!) object
        user = user
        text = text to check for suspicious content

        Example:
        is_suspicous = SuspiciousInput.check_input(content_object=post,
    user=post.user, text=post.body)

    """

    text = models.CharField(max_length=200, verbose_name="suspicious user input")
    user = models.ForeignKey(
        User, verbose_name="related user", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType, verbose_name="related model", on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["content_type_id"]
        default_permissions = (
            "change",
            "delete",
        )

    def __str__(self):
        return self.text

    def clean(self):
        # Cleaning fields
        max_chars = self._meta.get_field("text").max_length
        if len(self.text) >= max_chars:
            # Truncate the text to fit with max_length of field
            # otherwise a Database error is thrown
            self.text = self.text[:max_chars]

    def is_suspicious(self):
        if any(x in self.text.lower() for x in settings.ANTI_SPAM_KWRDS):
            return True
        if re.search(settings.ANTI_SPAM_PHONE_NR, self.text):
            return True
        # If this is the first post of this user check if it contains a link
        # Only for forum posts
        if self.content_type.model == "post":
            if self.user.posts.count() == 1:
                if "http" in self.text:
                    return True
        return False

    @classmethod
    def check_input(cls, *args, **kwargs):
        user_input = cls(*args, **kwargs)
        is_spam = user_input.is_suspicious()
        if is_spam:
            try:
                user_input.clean()
                user_input.save()
            except:
                pass

        return is_spam
