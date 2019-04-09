# Create your views here.

from models import Category
from django.views.generic.list import ListView

class CategoryList(ListView):
    queryset = Category.objects.order_by('-name')
    template_name = 'wlscreens/index.html'
    context_object_name = 'categories'
