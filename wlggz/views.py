# Create your views here.


from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from .forms import EditGGZForm
from .models import GGZAuth


@login_required
def change_password(request):
    """Set the online gaming password.

    The GGZAuth row is only created when a password is actually saved.
    """
    instance = GGZAuth.objects.filter(user=request.user).first()
    if instance is None:
        instance = GGZAuth(user=request.user)

    if request.method == "POST":
        form = EditGGZForm(request.POST, instance=instance, files=request.FILES)

        if form.is_valid():
            form.save()
            messages.info(request, "Your password was saved successfully.")

            return HttpResponseRedirect(reverse("profile_view"))
    else:
        form = EditGGZForm(instance=instance)

    template_params = {
        "ggz_form": form,
    }

    return render(request, "wlggz/edit_ggz.html", template_params)
