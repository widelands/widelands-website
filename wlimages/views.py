from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import Image
from .forms import UploadImageForm


def display(request, image, revision):
    revision = int(revision)

    img = get_object_or_404(Image, name=image, revision=revision)

    extension = img.image.path[-3:].lower()
    if extension not in ("png", "gif", "jpg", "bmp"):
        extension = "png"

    r = HttpResponse()
    r["Content-Type"] = "image/%s" % extension
    r.write(img.image.read())

    return r


@login_required
def upload(request, content_type, object_id, next="/"):
    if request.method == "POST":
        # A form bound to the POST data
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            Image.objects.create_and_save_image(
                user=request.user,
                image=request.FILES["imagename"],
                content_type=ContentType.objects.get(pk=content_type),
                object_id=object_id,
            )
            return HttpResponseRedirect(next)  # Redirect after POST
    else:
        form = UploadImageForm()  # An unbound form

    # Get the App (model) to which this image belongs to:
    app = ContentType.objects.get(id=content_type)
    # Get the current object's name (provided by __str__()) from this model
    name = app.get_object_for_this_type(id=object_id)

    return render(
        request,
        "wlimages/upload.html",
        {
            "upload_form": form,
            "referer": name,
        },
    )
