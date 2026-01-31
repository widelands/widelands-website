# -*- coding: utf-8 -*-

from django import template
from django.utils.encoding import force_str
from django.utils.text import slugify
from tagging.models import TaggedItem
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.filter
def restore_commandsymbols(s):
    """We need to restore " " for textile to work properly."""
    s = s.replace("&quot;", '"')
    s = s.replace("&quot;", '"')
    return force_str(s)


restore_commandsymbols.is_safe = True


@register.inclusion_tag("wiki/article_content.html")
def render_content(article, content_attr="content"):
    """Display the body of an article, rendered with Markdown.

    - content_attr is the article attribute that will be rendered.

    Use examples on templates:

        {# article have a content attribute #}
        {% render_content article %}

        {# article have a body attribute #}
        {% render_content article 'body' %}

        {# we want to display the summary instead #}
        {% render_content article 'summary' %}

    """
    return {
        "content": getattr(article, content_attr),
    }


@register.inclusion_tag("wiki/inlines/alphabet_list.html")
def alphabet_links(objects, sep=" |"):
    """Renders a template showing an alphabet list as links."""

    alphabet = {}
    for object in objects:
        if object.title[0].upper() not in alphabet:
            alphabet.update({object.title[0].upper(): slugify(object.title)})
    return {
        "alphabet": alphabet,
        "sep": sep,
    }


@register.inclusion_tag("wiki/inlines/tag_urls.html")
def tag_links(cur_tag=None, sep=" |"):
    """Renders a template showing all used tags in wiki.

    Workaround for bug: https://github.com/jazzband/django-tagging/pull/2
    """

    all_tags = []
    articles_ct = ContentType.objects.get(app_label="wiki", model="article")
    qs = TaggedItem.objects.filter(content_type=articles_ct).select_related("tag")

    for item in qs:
        if item.tag not in all_tags and item.tag.name != cur_tag:
            all_tags.append(item.tag)

    return {
        "tag_list": all_tags,
        "sep": sep,
    }
