from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from wiki.models import Article

from .models import Image
from .forms import UploadImageForm


def display(request, image, revision):
    revision = int(revision)

    img = get_object_or_404(Image, name=image, revision=revision)

    extension = img.image.path[-3:].lower()
    if extension not in ("png", "gif", "jpg", "bmp"):
        extension = "png"

    r = HttpResponse()
    r["Content-Type"] = f"image/{extension}"
    r.write(img.image.read())

    return r


@login_required
def upload(request, content_type, object_id, next="/"):
    # Images can only be attached to wiki articles the user may edit
    article_ct = ContentType.objects.get_for_model(Article)
    if int(content_type) != article_ct.pk:
        raise Http404
    article = get_object_or_404(Article, pk=object_id)
    if article.deleted and not request.user.is_staff:
        raise Http404

    edit_url = reverse(
        "wiki_edit_deleted" if article.deleted else "wiki_edit",
        kwargs={"title": article.title},
    )
    if not url_has_allowed_host_and_scheme(
        next, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next = edit_url

    if request.method == "POST":
        # A form bound to the POST data
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():  # All validation rules pass
            Image.objects.create_and_save_image(
                user=request.user,
                image=request.FILES["imagename"],
                content_type=article_ct,
                object_id=article.pk,
            )
            return HttpResponseRedirect(next)  # Redirect after POST
    else:
        form = UploadImageForm()  # An unbound form

    return render(
        request,
        "wlimages/upload.html",
        {
            "upload_form": form,
            "back_url": next,
        },
    )
