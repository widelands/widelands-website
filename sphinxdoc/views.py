# encoding: utf-8

import datetime
import os.path

from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
#from django.utils import simplejson as json
import json
from django.views import static

from sphinxdoc.models import App


SPECIAL_TITLES = {
    'genindex': 'General Index',
    'modindex': 'Module Index',
    'search': 'Search',
}


def documentation(request, slug, url):
    app = get_object_or_404(App, slug=slug)
    url = url.strip('/')
    page_name = os.path.basename(url)
    
    path = os.path.join(app.path, url, 'index.fjson')
    if not os.path.exists(path):
        path = os.path.dirname(path) + '.fjson'
        if not os.path.exists(path):
            raise Http404('"%s" does not exist' % path)

    templates = (
        'sphinxdoc/%s.html' % page_name,
        'sphinxdoc/documentation.html',
    )
    
    data = {
        'app': app,
        'doc': json.load(open(path, 'rb')),
        'env': json.load(open(
                os.path.join(app.path, 'globalcontext.json'), 'rb')),
        'version': app.name,
        'docurl': url,
        'update_date':  datetime.datetime.fromtimestamp(
                os.path.getmtime(os.path.join(app.path, 'last_build'))),
        'home': app.get_absolute_url(),
        # 'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
        'redirect_from': request.GET.get('from', None),
    
    }
    if 'title' not in data['doc']:
        data['doc']['title'] = SPECIAL_TITLES[page_name]
        
    return render_to_response(templates, data,
            context_instance=RequestContext(request))

def search(request, slug):
    from django.http import HttpResponse
    return HttpResponse('Not yet implemented.')
    
def objects_inventory(request, slug):
    app = get_object_or_404(App, slug=slug)
    response = static.serve(
        request, 
        document_root = app.path,
        path = "objects.inv",
    )
    response['Content-Type'] = "text/plain"
    return response

def images(request, slug, path):
    app = get_object_or_404(App, slug=slug)
    return static.serve(
        request, 
        document_root = os.path.join(app.path, '_images'),
        path = path,
    )
    
def source(request, slug, path):
    app = get_object_or_404(App, slug=slug)
    return static.serve(
        request,
        document_root = os.path.join(app.path, '_sources'),
        path = path,
    )
