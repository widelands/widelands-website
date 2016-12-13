from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from models import Poll, Choice, Vote
from django.views import generic


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'wlpoll/poll_detail.html'


# class ResultsView(generic.DetailView):
#    model = Poll
#    template_name = 'polls/results.html'

@login_required
def vote(request, object_id, next=None):
    if request.method == 'GET':
        return HttpResponseNotAllowed(['POST'])

    p = get_object_or_404(Poll, pk=object_id)

    user = request.user
    if user.poll_votes.filter(poll=p):
        return HttpResponseForbidden("Can't vote more than once")

    if not p.is_closed() and 'choice_id' in request.POST:
        c = get_object_or_404(Choice, pk=int(
            request.POST['choice_id']), poll=p)

        c.votes += 1
        c.save()

        v = Vote.objects.create(
            user=user,
            poll=p,
            choice=c
        )
        v.save()

    return HttpResponseRedirect(reverse('wlpoll_detail', args=(p.id,)))
