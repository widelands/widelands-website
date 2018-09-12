# Create your views here.


from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.conf import settings

from forms import EditProfileForm


@login_required
def delete_me(request):
    """Show a page to inform the user what deleting means."""

    context = {
        'user': request.user
    }
    return render(request, 'wlprofile/delete_me.html',
                  context)


@login_required
def do_delete(request):
    """Delete user specific data.

    We can't really delete a user who has posted some valid posts (no spam) because otherwise
    we have foreign keys constraints in the database. All we can do is to do some cleanup and
    anonymization.
    """

    from django.contrib.auth import logout
    from wlprofile.models import Profile
    from notification.models import NoticeSetting

    user = get_object_or_404(User, username=request.user)

    # Log the user out. We do this as early as possible but after
    # we get the User object.
    logout(request)

    # Clean the Online gaming password
    from wlggz.models import GGZAuth
    try:
        ggz_user = GGZAuth.objects.get(user=user)
        ggz_user.delete()
    except:
        pass

    # Clean the profile
    profile = user.wlprofile
    upload_to = Profile._meta.get_field('avatar').upload_to
    
    if upload_to in profile.avatar.name:
        # Delete the avatar file
        profile.avatar.delete()
    
    # Delete the profile and recreate it to get a clean profile page
    # We create a new one to have the anymous.png as avatar
    profile.delete()
    profile = Profile(user=user)
    profile.save()

    # Deactivate all subscriptions
    notice_settings = NoticeSetting.objects.filter(user=user)
    for setting in notice_settings:
        setting.send = False
        setting.save()

    # Put all PMs in the trash of the user. They stay as long in the trash until the sender or recipient
    # has also put the message in the trash.
    from django_messages.models import Message
    from datetime import datetime
    messages = Message.objects.inbox_for(user)
    for message in messages:
        message.recipient_deleted_at = datetime.now()
        message.save()
    messages = Message.objects.outbox_for(user)
    for message in messages:
        message.sender_deleted_at = datetime.now()
        message.save()

    # Do some settings in django.auth.User
    user.is_active = False
    user.is_staff = False
    user.is_superuser = False
    user.email = settings.DELETED_MAIL_ADDRESS
    user.save()
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
