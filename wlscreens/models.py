from django.db import models

from django.template.defaultfilters import slugify
from PIL import Image
from PIL.Image import core as _imaging
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.core.files.storage import FileSystemStorage
import os
from settings import THUMBNAIL_SIZE, MEDIA_ROOT

# Taken from django snippet 976

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to."""
        # If the filename already exists, remove it as if it was a true file
        # system
        if self.exists(name):
            os.remove(os.path.join(MEDIA_ROOT, name))
        return name


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super(Category, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('wlscreens_category', None, {'category_slug': self.slug})

    def __unicode__(self):
        return u"%s" % self.name


def screenshot_path(instance, filename):
    return 'wlscreens/screens/%s/%s.%s' % (
            instance.category, instance.name, filename.rsplit('.', 1)[-1].lower()
            )


def thumbnail_path(instance, filename):
    return 'wlscreens/thumbs/%s/%s.png' % (
            instance.category, instance.name)


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
    category = models.ForeignKey(Category, related_name='screenshots')

    class Meta:
        unique_together = ('name', 'category')

    def save(self, *args, **kwargs):
        # Open original screenshot which we want to thumbnail using PIL's Image
        # object
        image = Image.open(self.screenshot)

        # Convert to RGB if necessary
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)

        # Save to the thumbnail field
        suf = SimpleUploadedFile(os.path.split(self.screenshot.name)[-1],
                                 temp_handle.read(), content_type='image/png')
        self.thumbnail.save(suf.name + '.png', suf, save=False)

        # Save this photo instance
        super(Screenshot, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s:%s" % (self.category.name, self.name)
