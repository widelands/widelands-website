from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

class Image(models.Model):
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

    # objects = ThreadedCommentManager()
    # public = PublicThreadedCommentManager()
   
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


