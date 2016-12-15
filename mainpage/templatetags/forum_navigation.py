from pybb.models import Category
from django import template


register = template.Library()

@register.inclusion_tag('mainpage/forum_navigation.html')
def forum_navigation():
    """Makes the forum list available to the navigation, even
    if it is not loaded directly.

    Ordering:
    1.: value of 'Position' in pybb.Category
    2.: value of 'Position' of pybb.Forum.

    """
    categories = Category.objects.all()
    return {'categories': categories}
