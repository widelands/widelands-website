# Create your views here.

from .models import Category
from django.views.generic.list import ListView

class CategoryList(ListView):
    model = Category
    template_name = 'wlscreens/index.html'
    context_object_name = 'categories'
