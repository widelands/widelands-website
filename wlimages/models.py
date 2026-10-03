from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from datetime import datetime


class ImageManager(models.Manager):
    """We overwrite the defaults manager to make sure that the create function
    checks for validity.

    We also include some convenience functions here

    """

    def has_image(self, image_name):
        return bool(self.filter(name=image_name).count())

    def create(self, **keyw):
        """Makes sure that no image/revision pair is already in the
        database."""

        if "name" not in keyw or "revision" not in keyw:
            raise IntegrityError("needs name and revision as keywords")

        if self.filter(name=keyw["name"], revision=keyw["revision"]).count():
            raise Image.AlreadyExisting()

        return super(ImageManager, self).create(**keyw)

    def create_and_save_image(self, user, image, content_type, object_id):
        im = self.create(
            content_type=content_type,
            object_id=object_id,
            user=user,
            revision=1,
            name=image.name,
        )
        # The storage sanitizes the file name and picks a free one, so an
        # upload never overwrites the file of another image.
        im.image.save(image.name, image)


class Image(models.Model):
    class AlreadyExisting(IntegrityError):
        def __str__(self):
            return "The combination of image/revision is already in the database"

    """
    TODO
    """
    # Generic Foreign Key Fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    name = models.CharField(max_length=100)
    revision = models.PositiveIntegerField()

    # User Field
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Date Fields
    date_submitted = models.DateTimeField(
        _("date/time submitted"), default=datetime.now
    )
    image = models.ImageField(upload_to="wlimages/")

    objects = ImageManager()

    def __str__(self):
        return self.name

    def get_content_object(self):
        """
        taken from threadedcomments:

        Wrapper around the GenericForeignKey due to compatibility reasons
        and due to ``list_display`` limitations.
        """
        return self.content_object

    class Meta:
        ordering = ("-date_submitted",)
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        get_latest_by = "date_submitted"
