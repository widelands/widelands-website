from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from models import Image
from settings import MEDIA_ROOT
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from forms import UploadImageForm


def get_real_ip(request):
    """ Returns the real user IP, even if behind a proxy.
    Set BEHIND_PROXY to True in your settings if Django is
    running behind a proxy.
    """
    if getattr(settings, 'BEHIND_PROXY', False):
        return request.META['HTTP_X_FORWARDED_FOR']
    return request.META['REMOTE_ADDR']

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

    return render_to_response('wlimages/upload.html', {
        'upload_form': form,
    }, context_instance=RequestContext(request))

