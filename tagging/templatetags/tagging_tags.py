from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Variable
from django.utils.translation import gettext as _

from tagging.models import Tag

register = Library()


class TagsForObjectNode(Node):
    def __init__(self, obj, context_var):
        self.obj = Variable(obj)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = Tag.objects.get_for_object(
            self.obj.resolve(context)
        )
        return ""


@register.tag("tags_for_object")
def do_tags_for_object(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with an object and
    stores them in a context variable.

    Usage::

       {% tags_for_object [object] as [varname] %}

    Example::

        {% tags_for_object foo_object as tag_list %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(
            _("%s tag requires exactly three arguments") % bits[0]
        )
    if bits[2] != "as":
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return TagsForObjectNode(bits[1], bits[3])
