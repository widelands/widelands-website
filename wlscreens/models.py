from django.db import models

from django.template.defaultfilters import slugify
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings


# Taken from django snippet 976


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to."""
        # If the filename already exists, remove it as if it was a true file
        # system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ["-name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


def screenshot_path(instance, filename):
    return f"wlscreens/screens/{instance.category}/{instance.name}.{filename.rsplit('.', 1)[-1].lower()}"


def thumbnail_path(instance, filename):
    return f"wlscreens/thumbs/{instance.category}/{instance.name}.png"


class Screenshot(models.Model):
    name = models.CharField(max_length=255)

    screenshot = models.ImageField(
        upload_to=screenshot_path,
        storage=OverwriteStorage(),
    )
    thumbnail = models.ImageField(
        upload_to=thumbnail_path,
        editable=False,
        storage=OverwriteStorage(),
    )
    comment = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        related_name="screenshots",
        on_delete=models.CASCADE,
    )
    position = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        help_text="The position inside the category",
    )

    class Meta:
        unique_together = ("name", "category")
        ordering = ["-category__name", "position"]

    def save(self, *args, **kwargs):
        # Open original screenshot which we want to thumbnail using PIL's Image
        # object
        try:
            image = Image.open(self.screenshot)

            # As of now, the uploaded image is of PngImageFile. PIL relies that
            # this file is around in the future when we want to do anything
            # with its data. That is not guaranteed here though, because this
            # is a temporary file that django will delete at some point in
            # time. We convert it into an in-memory file here to avoid this
            # problem, in the same step we fix its mode to be RGB.
            image = image.convert("RGB")

            image.thumbnail(settings.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

            # Save the thumbnail
            temp_handle = BytesIO()
            image.save(temp_handle, "png")
            image.close()
            temp_handle.seek(0)

            # Save to the thumbnail field
            suf = SimpleUploadedFile(
                os.path.split(self.screenshot.name)[-1],
                temp_handle.read(),
                content_type="image/png",
            )
            self.thumbnail.save(suf.name + ".png", suf, save=False)

            # Save this photo instance
            super(Screenshot, self).save(*args, **kwargs)
        except IOError:
            # Likely we have a screenshot in the database which didn't exist
            # on the filesystem at the given path. Ignore it.
            pass

    def __str__(self):
        return f"{self.category.name}:{self.name}"
