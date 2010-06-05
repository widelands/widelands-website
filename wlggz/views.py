# Create your views here.


from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from forms import EditGGZForm

import settings
import ggz_models

# Settings
@login_required
def view(request, user = None):
    """
    empty text
    """


    if user is None:
        u = request.user
    else:
        u = User.objects.get( username = user )

    wlggz = u.wlggz
    wlggzstats = u.wlggzstats
    matches = u.wlggz_matches.order_by('-id')[:10]
    wonmatches = u.wlggz_matchwins.order_by('-id')[:10]

    #else:
    #    wlggz = User.objects.get( username = user ).wlggz
    #    wlggzstats = User.objects.get( username = user ).wlggzstats
    #    matches = User.objects.get( username = user ).wlggz_matches.order_by('-id')[:10]
    #    wonmatches = User.objects.get( username = user ).wlggz_matchwins.order_by('-date')[:10]

    template_params = {
        "ggzauth": wlggz,
        "ggzstats": wlggzstats,
        "ggzmatches": matches,
        "ggzwonmatches": wonmatches,
    }

    return render_to_response("wlggz/view_gzz_test.html",
                              template_params,
                              context_instance=RequestContext(request))

def view_ranking(request):
    """
    empty text
    """

    stats = ggz_models.GGZStats.objects.order_by('-rating')[:10]

    template_params = {
        "ggzstats": stats,
    }

    return render_to_response("wlggz/view_highscore.html",
                              template_params,
                              context_instance=RequestContext(request))

@login_required
def change_password(request):
    """
    empty text
    """
    instance = request.user.wlggz

    if request.method == 'POST':
        form = EditGGZForm(request.POST,
                    instance=instance, files = request.FILES)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse(view))
    else:
        form = EditGGZForm(instance=instance)

    template_params = {
        "wlggz": instance,
        "ggz_form": form,
    }

    return render_to_response("wlggz/edit_ggz.html",
                              template_params,
                              context_instance=RequestContext(request))
