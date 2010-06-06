# Create your views here.


from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.db import models

from forms import EditGGZForm

import settings
import ggz_models

def view_overview(request):
    return render_to_response("wlggz/view_ggz_overview.html",
                              context_instance=RequestContext(request))

def view_matches(request):
    
    try:
        matches = ggz_models.GGZMatches.objects.order_by('-date')[:10]
    except ggz_models.GGZMatches.DoesNotExist:
        matches = None

    template_params = {
        "ggzmatches": matches,
    }

    return render_to_response("wlggz/view_ggz_matches.html",
                              template_params,
                              context_instance=RequestContext(request))

# Settings
@login_required
def view(request, user = None):
    """
    empty text
    """

    template_params = {}

    try:
        if user is None:
            u = request.user
        else:
            u = User.objects.get( username = user )
        
        template_params["profile"] = u.wlprofile
    except User.DoesNotExist:
        u = None

    if u:
        try:
            template_params["ggzauth"] = u.wlggz
        except ggz_models.GGZauth.DoesNotExist:
            pass
        try:
            wlggzstats = u.wlggzstats
            matches = u.wlggz_matches.order_by('-id')[:10]
            wonmatches = u.wlggz_matchwins.order_by('-id')[:10]
            template_params["ggzstats"] = wlggzstats
            template_params["ggzmatches"] = matches
            template_params["ggzwonmatches"] = wonmatches
        except (ggz_models.GGZStats.DoesNotExist):
            pass

    return render_to_response("wlggz/view_ggz_test.html",
                              template_params,
                              context_instance=RequestContext(request))

def view_ranking(request):
    """
    empty text
    """

    try:
        stats = ggz_models.GGZStats.objects.order_by('-rating')[:10]
    except (ggz_models.GGZStats.DoesNotExist):
        stats = None

    template_params = {
        "ggzstats": stats,
    }

    return render_to_response("wlggz/view_ggz_highscore.html",
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
