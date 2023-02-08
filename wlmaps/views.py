#!/usr/bin/env python -tt
# encoding: utf-8
#
import os

from .forms import UploadMapForm, EditCommentForm
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    JsonResponse,
    HttpResponseBadRequest,
)
from django.urls import reverse
from django.conf import settings
from . import filters, models
from mainpage.wl_utils import get_pagination


#########
# Views #
#########
class MapList(ListView):
    model = models.Map

    @property
    def filter(self):
        if not hasattr(self, "_filter"):
            get = self.request.GET.copy()
            if not get.get("o"):
                get["o"] = "-pub_date"

            self._filter = filters.MapFilter(get, queryset=super().get_queryset())

        return self._filter

    def get_queryset(self):
        return self.filter.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "filter": self.filter,
            }
        )
        ctx.update(
            get_pagination(self.request, ctx["object_list"], settings.MAPS_PER_PAGE)
        )
        return ctx

    def options(self, request, *args, **kwargs):
        if request.is_ajax():
            q = request.GET.get("q", "")
            f = request.GET.get("f", "")

            if f == "uploader":
                values = (
                    User.objects.exclude(is_active=False)
                    .filter(username__icontains=q)
                    .values_list("username")
                )
            elif f == "author":
                # convert to set and back to list because distinct is not supported with sqlite
                values = list(
                    set(
                        models.Map.objects.filter(author__icontains=q)
                        .order_by("author")
                        .values_list("author", flat=True)
                    )
                )
            else:
                return HttpResponseBadRequest()

            return JsonResponse(list(map(lambda x: {"value": x}, values)), safe=False)
        else:
            return HttpResponseBadRequest()


def download(request, map_slug):
    """Very simple view that just returns the binary data of this map and
    increases the download count."""
    m = get_object_or_404(models.Map, slug=map_slug)

    file = open(m.file.path, "rb")
    data = file.read()
    filename = os.path.basename("%s.wmf" % m.name)

    # Remember that this has been downloaded
    m.nr_downloads += 1
    m.save(update_fields=["nr_downloads"])

    response = HttpResponse(data, content_type="application/octet-stream")
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename

    return response


def view(request, map_slug):
    map = get_object_or_404(models.Map, slug=map_slug)
    context = {
        "map": map,
    }
    return render(request, "wlmaps/map_detail.html", context)


@login_required
def edit_comment(request, map_slug):
    map = get_object_or_404(models.Map, slug=map_slug)
    if request.method == "POST":
        form = EditCommentForm(request.POST)
        if form.is_valid():
            map.uploader_comment = form.cleaned_data["uploader_comment"]
            map.save(update_fields=["uploader_comment"])
            return HttpResponseRedirect(map.get_absolute_url())
    else:
        form = EditCommentForm(instance=map)

    context = {"form": form, "map": map}

    return render(request, "wlmaps/edit_comment.html", context)


@login_required
def upload(request):
    if request.method == "POST":
        form = UploadMapForm(request.POST, request.FILES)
        if form.is_valid():
            map = form.save(commit=False)
            map.uploader = request.user
            map.save()
            return HttpResponseRedirect(map.get_absolute_url())
    else:
        form = UploadMapForm()

    context = {
        "form": form,
    }
    return render(request, "wlmaps/upload.html", context)
