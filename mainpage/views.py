from django.shortcuts import render_to_response
from django.template import RequestContext

def mainpage(request):
    return render_to_response('mainpage.html', context_instance=RequestContext(request))

