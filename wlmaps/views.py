#!/usr/bin/env python -tt
# encoding: utf-8
#

from forms import UploadMapForm, EditCommentForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
import models
from settings import MAPS_PER_PAGE
from wl_utils import get_real_ip
import os


#########
# Views #
#########
def index(request):
    maps = models.Map.objects.all()
    return render_to_response('wlmaps/index.html',
                              {'maps': maps,
                               'maps_per_page': MAPS_PER_PAGE,
                               },
                              context_instance=RequestContext(request))


def rate(request, map_slug):
    """Rate a given map."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['post'])

    m = get_object_or_404(models.Map, slug=map_slug)

    if not 'vote' in request.POST:
        return HttpResponseBadRequest()
    try:
        val = int(request.POST['vote'])
    except ValueError:
        return HttpResponseBadRequest()

    if not (0 < val <= 10):
        return HttpResponseBadRequest()

    m.rating.add(score=val, user=request.user,
                 ip_address=get_real_ip(request))
    
    # m.save() is not needed

    return HttpResponseRedirect(reverse('wlmaps_view', None, {'map_slug': m.slug}))


def download(request, map_slug):
    """Very simple view that just returns the binary data of this map and
    increases the download count."""
    m = get_object_or_404(models.Map, slug=map_slug)

    file = open(m.file.path, 'rb')
    data = file.read()
    filename = os.path.basename('%s.wmf' % m.name)

    # Remember that this has been downloaded
    m.nr_downloads += 1
    m.save()

    response = HttpResponse(data, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    return response


def view(request, map_slug):
    map = get_object_or_404(models.Map, slug=map_slug)
    context = {
        'map': map,
    }
    return render_to_response('wlmaps/map_detail.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
def edit_comment(request, map_slug):
    map = get_object_or_404(models.Map, slug=map_slug)
    if request.method == 'POST':
        form = EditCommentForm(request.POST)
        if form.is_valid():
            map.uploader_comment = form.cleaned_data['uploader_comment']
            map.save()
            return HttpResponseRedirect(map.get_absolute_url())
    else:
        form = EditCommentForm(instance=map)

    context = {'form': form, 'map': map}

    return render_to_response('wlmaps/edit_comment.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadMapForm(request.POST, request.FILES)
        if form.is_valid():
            map = form.save(commit=False)
            map.uploader = request.user
            map.save()
            return HttpResponseRedirect(map.get_absolute_url())
    else:
        form = UploadMapForm()

    context = {'form': form, }
    return render_to_response('wlmaps/upload.html',
                              context,
                              context_instance=RequestContext(request))
