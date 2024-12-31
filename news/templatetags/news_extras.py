from django import template
from django.apps import apps

import re

Post = apps.get_model("news", "post")
Category = apps.get_model("news", "category")

register = template.Library()


class LatestPosts(template.Node):
    def __init__(self, limit, var_name):
        self.limit = limit
        self.var_name = var_name

    def render(self, context):
        posts = Post.objects.published()[: int(self.limit)]
        if posts and (int(self.limit) == 1):
            context[self.var_name] = posts[0]
        else:
            context[self.var_name] = posts
        return ""


@register.tag
def get_latest_posts(parser, token):
    """Gets any number of latest posts and stores them in a varable.

    Syntax::

        {% get_latest_posts [limit] as [var_name] %}

    Example usage::

        {% get_latest_posts 10 as latest_post_list %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%s tag requires arguments" % token.contents.split()[0]
        )
    m = re.search(r"(.*?) as (\w+)", arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    format_string, var_name = m.groups()
    return LatestPosts(format_string, var_name)
