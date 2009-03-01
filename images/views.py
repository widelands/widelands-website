from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from models import Image
from settings import MEDIA_ROOT

def display( request, image, revision ):
    print "revision:", revision
    print "image:", image

    
    revision = int(revision)

    img = get_object_or_404( Image, name = image, revision = revision )
    
    extension = img.image.path[-3:].lower()
    if extension not in ("png","gif","jpg","bmp"):
        extension = "png"

    r = HttpResponse()
    r['Content-Type'] = 'image/%s' % extension
    r.write(img.image.read())

    return r


