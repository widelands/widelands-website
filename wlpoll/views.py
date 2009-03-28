from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import Poll, Choice

def vote(request, object_id, next = None):
    if request.method == "GET":
        return HttpResponseNotAllowed(["POST"])
    
    p = get_object_or_404(Poll,pk=object_id)

    if not p.is_closed() and "choice_id" in request.POST:
        c = get_object_or_404(Choice, pk=int(request.POST["choice_id"]),poll=p)
        
        c.votes += 1
        c.save()
        
    return HttpResponseRedirect(reverse("wlpoll_detail", args = (p.id,)))
