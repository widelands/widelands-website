from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from models import Image
from wl_utils import get_real_ip
from forms import UploadImageForm

def display( request, image, revision ):
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
def upload(request,content_type,object_id, next="/"):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            Image.objects.create_and_save_image(user=request.user,image=request.FILES["imagename"],
                        content_type=ContentType.objects.get(pk=content_type),object_id=object_id, ip=get_real_ip(request))
            return HttpResponseRedirect(next) # Redirect after POST
    else:
        form = UploadImageForm() # An unbound form
    
    # Get the App (model) to which this image belongs to:
    app = ContentType.objects.get(id=content_type)
    # Get the current object's name (provided by __unicode__()) from this model
    name = app.get_object_for_this_type(id=object_id)

    return render_to_response('wlimages/upload.html', {
        'upload_form': form,
        'referer': name,
    }, context_instance=RequestContext(request))

