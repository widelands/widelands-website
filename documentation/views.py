from django.http import HttpResponse
from django.shortcuts import redirect

# !!! Only call this view from local_urls.py !!!


def dirhtml_view(request, folder_name=None):
    """Workaround to prevent Http404 'directory indexes are not allowed' raised
    by django.views.static.serve when using 'dirhtml' as builder for the
    sphinxdoc documentation."""

    if folder_name is None:
        path = "index.html"
    else:
        path = "/documentation/" + folder_name + "/index.html"

    return redirect(path)
