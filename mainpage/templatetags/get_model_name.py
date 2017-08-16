from django import template

register = template.Library()

@register.filter
def get_model_name(value):
    """Returns the name of a model"""
    return value.__class__.__name__