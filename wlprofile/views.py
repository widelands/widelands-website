# Create your views here.


from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from forms import EditProfileForm
import settings

# Settings
@login_required
def view(request, user = None):
    """
    View the profile. Note that login is required here
    to make sure that not all spam post can harvest here
    """
    if user is None:
        profile = request.user.wlprofile
    else:
        profile = User.objects.get( username = user ).wlprofile
    
    template_params = {
        "profile": profile,
    }

    return render_to_response("wlprofile/view_profile.html",
                              template_params,
                              context_instance=RequestContext(request))

@login_required
def edit(request):
    instance = request.user.wlprofile

    if request.method == 'POST':
        form = EditProfileForm(request.POST,
                    instance=instance, files = request.FILES)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse(view))
    else:
        form = EditProfileForm(instance=instance)

    template_params = {
        "profile": instance,
        "profile_form": form,
    }
    return render_to_response("wlprofile/edit_profile.html",
                              template_params,
                              context_instance=RequestContext(request))


