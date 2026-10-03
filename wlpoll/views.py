from django.db import IntegrityError, transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.urls import reverse
from .models import Poll, Choice, Vote
from django.views import generic


class DetailView(generic.DetailView):
    model = Poll
    template_name = "wlpoll/poll_detail.html"


# class ResultsView(generic.DetailView):
#    model = Poll
#    template_name = 'polls/results.html'


@login_required
def vote(request, object_id, next=None):
    if request.method == "GET":
        return HttpResponseNotAllowed(["POST"])

    p = get_object_or_404(Poll, pk=object_id)

    user = request.user
    if user.poll_votes.filter(poll=p):
        return HttpResponseForbidden("Can't vote more than once")

    try:
        choice_id = int(request.POST["choice_id"])
    except KeyError, ValueError:
        choice_id = None

    if not p.is_closed() and choice_id is not None:
        c = get_object_or_404(Choice, pk=choice_id, poll=p)

        try:
            with transaction.atomic():
                Vote.objects.create(user=user, poll=p, choice=c)
                Choice.objects.filter(pk=c.pk).update(votes=F("votes") + 1)
        except IntegrityError:
            # A parallel request of this user has voted already
            return HttpResponseForbidden("Can't vote more than once")

    return HttpResponseRedirect(reverse("wlpoll_detail", args=(p.id,)))
