# Create your views here.

from models import Category, Screenshot
from django.shortcuts import render
from django.http import Http404


def index(request):
    c = Category.objects.order_by('-name')

    return render(request, 'wlscreens/index.html',
                  {'categories': c, }
                  )


def category(request, category_slug):
    """Not implemented at the moment."""

    raise Http404
