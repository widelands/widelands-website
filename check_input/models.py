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

    def strip_text(self, name="SPAM FOUND", spam_start=0, spam_end=0):
        """Strip the text to fit with the text field of the model.

        name        = name of check
        spam_start  = position inside the string where spam starts
        end_spam    = position inside the string where spam ends

        """

        which = "{}: …".format(name.upper())
        max_chars = self._meta.get_field("text").max_length - len(which) - 1
        spam_middle = ((spam_end - spam_start) // 2) + spam_start

        start_pos = end_pos = spam_middle
        tmp_text = ""

        # Calculate the string so that the found spam is in the middle
        while len(tmp_text) < max_chars and len(tmp_text) < len(self.text):
            if start_pos > 0:
                start_pos = start_pos - 1
            if end_pos < len(self.text):
                end_pos = end_pos + 1
            tmp_text = self.text[start_pos:end_pos]

        self.text = "{} {}".format(which, tmp_text)

    def is_suspicious(self):
        # check for keywords
        for x in SuspiciousKeyword.objects.as_list():
            if x in self.text.lower():
                pos = self.text.lower().find(x)
                self.strip_text(
                    name="Keyword spam", spam_start=pos, spam_end=pos + len(x)
                )
                return True

        # check for telephone nr
        match = re.search(settings.ANTI_SPAM_PHONE_NR, self.text)
        if match:
            self.strip_text(
                name="Telephonenr.", spam_start=match.start(), spam_end=match.end()
            )
            return True

        # If this is the first post of this user check if it contains a link
        # Only for forum posts
        if self.content_type.model == "post" and self.user.posts.count() == 1:
            match = re.search(PLAIN_LINK_RE, self.text)
            if match:
                self.strip_text(
                    name="Link in first post",
                    spam_start=match.start(),
                    spam_end=match.end(),
                )
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


class SuspiciousKeywordManager(models.Manager):
    def as_list(self):
        return [x.keyword for x in self.all()]


class SuspiciousKeyword(models.Model):

    keyword = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Spam Keyword",
        help_text="Type lowercase only, spaces allowed",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Keyword Description",
    )

    class Meta:
        verbose_name_plural = "Spam Keywords"

    objects = SuspiciousKeywordManager()

    def __str__(self):
        return self.keyword
