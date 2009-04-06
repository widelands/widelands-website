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
import os
from cStringIO import StringIO

from settings import WIDELANDS_SVN_DIR, MEDIA_ROOT, MEDIA_URL


#########
# Views #
#########
def index( request ):
    objects = models.Map.objects.all()
   
    return render_to_response("wlmaps/index.html", 
                { "object_list": objects, },
                context_instance = RequestContext(request))

def download( request, map_slug ):
    """
    Very simple view that just returns the binary data of this map and increases
    the download count
    """
    m = get_object_or_404( models.Map, slug = map_slug )

    data = open(m.file.path, "rb").read()
    
    m.nr_downloads += 1
    m.save()

    response =  HttpResponse( data, mimetype = "application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename("%s.wmf" % m.name)

    return response
    


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
    print "request.POST:", request.POST
    test = request.POST.get("test", False)
    comment = request.POST.get("comment",u"")
    

    if "mapfile" in request.FILES: 
        mf = request.FILES["mapfile"]
        
        mfdata = mf.read()

        m = WidelandsMap()
        try:
            m.load(StringIO(mfdata))
        except WlMapLibraryException:
            return JsonReply( 3, "Invalid Map File" )

        # Draw the minimaps
        mm = m.make_minimap(WIDELANDS_SVN_DIR)
        mm_path = "%s/wlmaps/minimaps/%s.png" % (MEDIA_ROOT,m.name)
        mm_url = "/wlmaps/minimaps/%s.png" % m.name
        file_path = "%s/wlmaps/maps/%s.wmf" % (MEDIA_ROOT,m.name)
        
        if not test:
            f = open(file_path,"wb")
            f.write(mfdata)
            f.close()
            scipy.misc.pilutil.imsave(mm_path, mm)
        

        # Create the map
        try:
            nm = models.Map.objects.create(
                name = m.name,
                author = m.author,
                w = m.w,
                h = m.h,
                nr_players = m.nr_players,
                descr = m.descr,
                minimap = mm_url,
                file = file_path,
                world_name = m.world_name,

                uploader = request.user,
                uploader_comment = comment,
            )
        except IntegrityError:
            return JsonReply(2, "Map with the same name already exists in database!")

        nm.save()
        return JsonReply(0, map_id = nm.pk )
    
    return JsonReply(1, "No mapfile in request!")
