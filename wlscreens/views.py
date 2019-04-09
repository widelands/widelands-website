# Create your views here.

from models import Category, Screenshot
from django.shortcuts import render
from django.http import Http404
from django.views.generic.list import ListView

class CategoryList(ListView):
    queryset = Category.objects.order_by('-name')
    template_name = 'wlscreens/index.html'
    context_object_name = 'categories'


def category(request, category_slug):
    """Not implemented at the moment."""

    raise Http404
