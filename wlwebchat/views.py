# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

def webchat(request):
    return render_to_response('wlwebchat/index.html', context_instance=RequestContext(request))

