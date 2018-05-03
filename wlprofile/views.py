# Create your views here.


from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect

from forms import EditProfileForm
import settings

# Settings


@login_required
def view(request, user=None):
    """View the profile.

    Note that login is required here to make sure that not all spam post
    can harvest here

    """
    if user is None:
        profile = request.user.wlprofile
    else:
        profile = User.objects.get(username=user).wlprofile

    template_params = {
        'profile': profile,
    }

    return render(request, 'wlprofile/view_profile.html',
                              template_params)


@login_required
def edit(request):
    instance = request.user.wlprofile

    if request.method == 'POST':
        form = EditProfileForm(request.POST,
                               instance=instance, files=request.FILES)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse(view))
    else:
        form = EditProfileForm(instance=instance)

    template_params = {
        'profile': instance,
        'profile_form': form,
    }
    return render(request, 'wlprofile/edit_profile.html',
                              template_params)
