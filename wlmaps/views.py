#!/usr/bin/env python -tt
# encoding: utf-8
#

from forms import UploadMapForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.db import IntegrityError
import models
from settings import MAPS_PER_PAGE

import os
import zipfile


#########
# Views #
#########
def index( request ):
    maps = models.Map.objects.all()
    return render_to_response("wlmaps/index.html",
                { "maps": maps,
                  "maps_per_page": MAPS_PER_PAGE,
                },
                context_instance = RequestContext(request))

def rate( request, map_slug ):
    """
    Rate a given map
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["post"])

    m = get_object_or_404( models.Map, slug = map_slug )

    if not "vote" in request.POST:
        return HttpResponseBadRequest()
    try:
        val = int(request.POST["vote"])
    except ValueError:
        return HttpResponseBadRequest()

    if not (0 < val <= 10):
        return HttpResponseBadRequest()

    m.rating.add(score=val, user=request.user,
                 ip_address=request.META['REMOTE_ADDR'])
    # m.save() is not needed

    return HttpResponseRedirect(reverse("wlmaps_view", None, {"map_slug": m.slug }))


def download( request, map_slug ):
    """
    Very simple view that just returns the binary data of this map and increases
    the download count
    """
    m = get_object_or_404( models.Map, slug = map_slug )

    file = open(m.file.path,"rb")
    data = file.read()

    # We have to find the correct filename, widelands is quite
    # buggy. The Filename must be the same as the directory
    # packed in the zip.
    file.seek(0)
    zf = zipfile.ZipFile(file)
    probable_filenames = filter( len, [ i.filename.split('/')[0] for i in zf.filelist ])
    if not len(probable_filenames):
        probable_filename = os.path.basename("%s.wmf" % m.name)
    else:
        probable_filename = probable_filenames[0]

    # Remember that this has been downloaded
    m.nr_downloads += 1
    m.save()

    response =  HttpResponse( data, mimetype = "application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename="%s"' % probable_filename

    return response


def view(request, map_slug):
    map = get_object_or_404( models.Map, slug = map_slug )

    context = {
        #"average_rating": _average_rating( map.rating ),
        "map": map,
    }
    return render_to_response( "wlmaps/map_detail.html",
                              context,
                              context_instance=RequestContext(request))


@login_required
def upload( request ):
    if request.method == 'POST':
        form = UploadMapForm(request.POST, request.FILES)
        if form.is_valid():
            map = form.save(commit=False)
            map.uploader = request.user
            map.save()
            return HttpResponseRedirect(map.get_absolute_url())
    else:
        form = UploadMapForm()

    context = { 'form': form, }
    return render_to_response( "wlmaps/upload.html",
                              context,
                              context_instance=RequestContext(request))
