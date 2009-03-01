from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from datetime import datetime

from settings import MEDIA_ROOT

# TEMP
from widelands.wiki.models import Article

class ImageManager(models.Manager):
    """
    We overwrite the defaults manager to make sure 
    that the create function checks for validity. We also include
    some convenience functions here
    """
    def has_image(self,image_name):
        return bool(self.filter(name=image_name).count())
           

    def create(self,**keyw):
        """
        Makes sure that no image/revision pair is already in the database
        """
        if "name" not in keyw or "revision" not in keyw:
            raise IntegrityError("needs name and revision as keywords")

        if self.filter(name=keyw["name"],revision=keyw["revision"]).count():
            raise Image.AlreadyExisting()
        
        return super(ImageManager,self).create(**keyw)

    def create_and_save_image(self,user,image):
        # if self.has_image(name):
        #     raise RuntimeError,"Image with name %s already exists. This is likely an Error" % name
        name = image.name.lower()
        im = self.create(content_type=ContentType.objects.get_for_model(Article), object_id=1, 
                    user=user,revision=1,name=name)

        # Image.objects.create(name=name,content_type=ContentType.objects.get_for_model(Article),
        #                      image="/images/%s" % name)
        path = "%s/images/%s" % (MEDIA_ROOT,image.name)
        print "path:", path

        destination = open(path,"wb")
        for chunk in image.chunks():
            destination.write(chunk)

        im.image = path

        im.save()


class Image(models.Model):
    class AlreadyExisting(IntegrityError):
        def __str__(self):
            return "The combination of image/revision is already in the database"

    """
    TODO
    """
    # Generic Foreign Key Fields
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey()
    
    name = models.CharField(max_length="100")
    revision = models.PositiveIntegerField()

    # User Field
    user = models.ForeignKey(User)
    ip_address = models.IPAddressField(_('IP address'), null=True, blank=True)
    
    # Date Fields
    date_submitted = models.DateTimeField(_('date/time submitted'), default = datetime.now)
    image = models.ImageField(upload_to="images/")

    objects = ImageManager()
   
    def __unicode__(self):
        return "Bildchen"

    def get_content_object(self):
        """
        taken from threadedcomments:

        Wrapper around the GenericForeignKey due to compatibility reasons
        and due to ``list_display`` limitations.
        """
        return self.content_object
    
    class Meta:
        ordering = ('-date_submitted',)
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        get_latest_by = "date_submitted"


