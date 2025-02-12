from django.utils.safestring import mark_safe
from django.utils.html import escape
from django import template


register = template.Library()


@register.simple_tag
def get_obj_link(object, anchor=""):
    """Return A tag with link to object."""

    rel_obj = object.content_type.get_object_for_this_type(pk=object.object_id)

    url = hasattr(rel_obj, "get_absolute_url") and rel_obj.get_absolute_url() or None
    return mark_safe('<a href="%s">%s</a>' % (url, escape(rel_obj)))
