from django import template

register = template.Library()

@register.filter
def get_model_name(object):
    """Returns the name of an objects model"""
    return object.__class__.__name__