# Create your views here.


from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from forms import EditProfileForm
import settings


@login_required
def delete_me(request):
    """Show a page to inform the user what deleting means."""

    context = {
        'user': request.user
    }
    return render(request, 'wlprofile/delete_me.html',
                  context)


def do_delete(request):
    """Delete user specific data.

    We can't delete a user but do some cleanup.  
    """

    from django.contrib.auth.models import User
    from django.contrib.auth import logout

    user = get_object_or_404(User, username=request.user)

    # Log the user out. This must be done as early as possible but after
    # we get the User object.
    logout(request)

    # Deleting the profile removes private settings, e.g. the avatar
    # TODO(franku): Delete also the image file (not the anonymus.png)
    profile = user.wlprofile
    profile.delete()

    # Deactivate all subscriptions
    from notification.models import NoticeSetting
    settings = NoticeSetting.objects.filter(user=user)
    for setting in settings:
        setting.send = False
        setting.save()

    # Remove written PMs from outbox
    from django_messages.models import Message
    messages = Message.objects.outbox_for(user)
    for message in messages:
        message.delete()
    # Remove PMs which are in the trash of sender and recipients
    messages = Message.objects.trash_for(user)
    for message in messages:
        message.delete()
    # TODO(franku): Prevend sending PMs to a deactivated user

    # Do some settings in Django
    user.is_active = False
    user.is_staff = False
    user.is_superuser = False
    user.email = 'deleted@wl.org'
    user.save()
    #return redirect('delete_me')
    return redirect('mainpage')


@login_required
def view(request, user=None):
    """View the profile.

    Note that login is required here to make sure that not all spam post
    can harvest here

    """
    if user is None:
        profile = request.user.wlprofile
    else:
        profile = get_object_or_404(User, username=user).wlprofile

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
