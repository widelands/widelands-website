from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import Poll, Choice

def view(request, poll_id ):
    p = get_object_or_404(Poll,pk=poll_id)
    
    template_data = {
        "poll": p,
    }

    return render_to_response('poll/view.html', 
            template_data,
            context_instance=RequestContext(request))

def vote(request, poll_id, next = None):
    pass

