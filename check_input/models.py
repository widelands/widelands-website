from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

from pybb.util import PLAIN_LINK_RE
import re


class SuspiciousInput(models.Model):
    """Model for collecting suspicious user input.

        Call the check_input method with these attributes:
        content_object = Model instance of a saved(!) object
        user = user
        text = text to check for suspicious content

        Example:
        is_suspicious = SuspiciousInput.check_input(content_object=post,
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

    def strip_text(self, which="SPAM FOUND", end=0):
        """Strip the text to fit with the text field.

        Add a small hint which check has found spam.

        """
        which = "{}: ".format(which.upper())
        max_chars = self._meta.get_field("text").max_length - len(which) - 1

        start = end - max_chars // 2
        end = end + max_chars // 2
        self.text = "{} {}".format(which, self.text[start:end])

    def is_suspicious(self):
        # check for keywords
        for x in settings.ANTI_SPAM_KWRDS:
            if x in self.text.lower():
                pos = self.text.lower().find(x)
                self.strip_text(which="Keyword spam", end=pos + len(x))
                return True

        # check for telephone nr
        match = re.search(settings.ANTI_SPAM_PHONE_NR, self.text)
        if match:
            self.strip_text(which="Telephonenr.", end=match.end())
            return True

        # If this is the first post of this user check if it contains a link
        # Only for forum posts
        if self.content_type.model == "post" and self.user.posts.count() == 1:
            match = re.search(PLAIN_LINK_RE, self.text)
            if match:
                self.strip_text(which="Link in first post", end=match.end())
                return True

        return False

    @classmethod
    def check_input(cls, *args, **kwargs):
        user_input = cls(*args, **kwargs)
        is_spam = user_input.is_suspicious()
        if is_spam:
            try:
                user_input.save()
            except ValidationError:
                pass

        return is_spam
