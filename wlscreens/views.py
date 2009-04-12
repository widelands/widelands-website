# Create your views here.

from models import Category, Screenshot
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404

def index( request ):
    c = Category.objects.all()
    
    return render_to_response( "wlscreens/index.html", 
                { "categories": c, },
                RequestContext(request) )

def category(request, category_slug):
    "Not implemented at the moment"

    raise Http404
