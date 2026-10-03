from functools import partial

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django_messages import views as messages_views
from django_messages_wl.forms import ExtendedComposeForm
from mainpage.wl_utils import is_ajax, username_suggestions
import json


@login_required
def compose(request, *args, **kwargs):
    """django_messages' compose with a form that knows the sender."""
    form_class = partial(ExtendedComposeForm, sender=request.user)
    return messages_views.compose(request, *args, form_class=form_class, **kwargs)


@login_required
def reply(request, *args, **kwargs):
    """django_messages' reply with a form that knows the sender."""
    form_class = partial(ExtendedComposeForm, sender=request.user)
    return messages_views.reply(request, *args, form_class=form_class, **kwargs)


@login_required
def get_usernames(request):
    """AJAX Callback for JS autocomplete.

    This is used for autocompletion of usernames when writing PMs.
    The path.name of this function has to be used in each place:
    1. Argument of source of the JS widget
    2. urls.py

    """
    if is_ajax(request):
        usernames = username_suggestions(request.GET.get("term", ""))
        results = []
        for user in usernames:
            name_json = {"value": user.username}
            results.append(name_json)
        data = json.dumps(results)
    else:
        data = "fail"
    mimetype = "application/json"
    return HttpResponse(data, mimetype)
