from django.contrib.auth.models import User
from django.http import HttpResponse
import json


def get_usernames(request):
    """AJAX Callback for JS autocomplete.

    This is used for autocompletion of usernames when writing PMs.
    The path.name of this function has to be used in each place:
    1. Argument of source of the JS widget
    2. urls.py

    """
    if request.is_ajax():
        q = request.GET.get("term", "")

        usernames = User.objects.exclude(is_active=False).filter(username__icontains=q)
        results = []
        for user in usernames:
            name_json = {"value": user.username}
            results.append(name_json)
        data = json.dumps(results)
    else:
        data = "fail"
    mimetype = "application/json"
    return HttpResponse(data, mimetype)
