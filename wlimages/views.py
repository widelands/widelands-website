from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from models import Image
from settings import MEDIA_ROOT
from django.core.files.uploadedfile import SimpleUploadedFile

from forms import UploadImageForm

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

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            Image.objects.create_and_save_image(user=request.user,image=request.FILES["image"])
            
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = UploadImageForm() # An unbound form

    return render_to_response('wlimages/upload.html', {
        'upload_form': form,
    })

