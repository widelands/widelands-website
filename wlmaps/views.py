#!/usr/bin/env python -tt
# encoding: utf-8
#

from forms import UploadMapForm
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.db import IntegrityError
import models

from widelandslib.Map import WidelandsMap, WlMapLibraryException 

import scipy

from settings import WIDELANDS_SVN_DIR, MEDIA_ROOT, MEDIA_URL


#########
# Views #
#########
def index( request ):
    pass

def view(request, map_slug):
    m = get_object_or_404( models.Map, slug = map_slug )
    
    context = {
        "object": m,
    }
    return render_to_response( "wlmaps/map_detail.html", 
                              context, 
                              context_instance=RequestContext(request))

@login_required
def upload( request ):
    """
    Uploads a map. This is an ajax post and returns an JSON object
    with the following values. 

    success_code - integer (0 means success else error)
    error_msg - if success_code = 1 this contains an descriptive error
    map_id - id of newly uploaded map
    """
    def JsonReply( success_code, error_msg = None, **kwargs):
        d = kwargs
        d['success_code'] = success_code
        if error_msg != None:
            d['error_msg'] = error_msg
        return HttpResponse( json.dumps(d), mimetype="application/javascript" )

    if request.method != "POST":
        return HttpResponseNotAllowed(["post"])
    
    form = UploadMapForm( request.POST )
    test = request.POST.get("test", False)

    if "mapfile" in request.FILES: 
        mf = request.FILES["mapfile"]
        
        m = WidelandsMap()
        try:
            m.load(mf)
        except WlMapLibraryException:
            return JsonReply( 3, "Invalid Map File" )

        # Draw the minimaps
        mm = m.make_minimap(WIDELANDS_SVN_DIR)
        mm_path = "%s/wlmaps/minimaps/%s.png" % (MEDIA_ROOT,m.name)
        mm_url = "/wlmaps/minimaps/%s.png" % m.name
        
        if not test:
            scipy.misc.pilutil.imsave(mm_path, mm)
        

        # Create the map
        try:
            nm = models.Map.objects.create(
                name = m.name,
                author = m.author,
                w = m.w,
                h = m.h,
                descr = m.descr,
                minimap = mm_url,
                world_name = m.world_name,

                uploader = request.user,
                uploader_comment = ""
            )
        except IntegrityError:
            return JsonReply(2, "Map with the same name already exists in database!")

        nm.save()
        return JsonReply(0, map_id = nm.pk )
    
    return JsonReply(1, "No mapfile in request!")
