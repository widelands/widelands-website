from django.db import models

from django.template.defaultfilters import slugify
import Image
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
import os  
from settings import THUMBNAIL_SIZE


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True, blank = True)
   
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        return super(Category,self).save(*args,**kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        return ("wlscreens_category", None, { "category_slug": self.slug } )

    def __unicode__(self):
        return u"%s" % self.name

class Screenshot(models.Model):
    name = models.CharField(max_length=256)
    
    screenshot = models.ImageField(
        upload_to= lambda i,n: "wlscreens/screens/%s/%s.%s" % (i.category,i.name,n.rsplit(".",1)[-1].lower()),
    )
    thumbnail = models.ImageField(
        upload_to= lambda i,n: "wlscreens/thumbs/%s/%s.png" % (i.category,i.name),
        editable = False,
    )
    comment = models.TextField( null = True, blank = True )
    category = models.ForeignKey( Category, related_name = "screenshots" )
    
    class Meta:
        unique_together = ("name","category")
   
    def save(self, *args, **kwargs):
      if self.screenshot and not isinstance(self.screenshot, UploadedFile):
          self.screenshot.delete(save=False)
      if self.thumbnail and not isinstance(self.thumbnail, UploadedFile):
          self.thumbnail.delete(save=False)

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
      self.thumbnail.save(suf.name+'.png', suf, save=False)
  
      # Save this photo instance
      super(Screenshot, self).save(*args,**kwargs)

    def __unicode__(self):
        return u"%s:%s" % (self.category.name,self.name)

        
