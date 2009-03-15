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
        form = EditProfileForm(request.POST, instance=instance)
         
        if form.is_valid():
            if "avatar" in request.FILES:
                a = request.FILES["avatar"]

                fn = "%s/wlprofile/avatars/%s.png" % (settings.MEDIA_ROOT,request.user.username)
                destination = open(fn, "wb")
                for chunk in a.chunks():
                    destination.write(chunk)
                destination.close()

                fn = "%s/wlprofile/avatars/%s.png" % (settings.MEDIA_URL,request.user.username)
                instance.avatar = fn 
                instance.save()

            form.save()
            
            return HttpResponseRedirect(reverse(view))
    form = EditProfileForm(instance=instance)
    print "form:", form
    print "instance:", instance

    template_params = {
        "profile_form": form,
    }
    return render_to_response("wlprofile/edit_profile.html",
                              template_params,
                              context_instance=RequestContext(request))


