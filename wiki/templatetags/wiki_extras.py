# -*- coding: utf-8 -*-

import re
from django import template
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.text import slugify


register = template.Library()


@register.filter
def restore_commandsymbols(s):
    """We need to restore " " for textile to work properly."""
    s = s.replace("&quot;", '"')
    s = s.replace("&quot;", '"')
    return force_text(s)


restore_commandsymbols.is_safe = True


@register.inclusion_tag("wiki/article_content.html")
def render_content(article, content_attr="content", markup_attr="markup"):
    """Display an the body of an article, rendered with the right markup.

    - content_attr is the article attribute that will be rendered.
    - markup_attr is the article atribure with the markup that used
      on the article. the choices are:
      - 'rst' for reStructuredText
      - 'mrk' for Markdown
      - 'txl' for Textile

    Use examples on templates:

        {# article have a content and markup attributes #}
        {% render_content article %}

        {# article have a body and markup atributes #}
        {% render_content article 'body' %}

        {# we want to display the  summary instead #}
        {% render_content article 'summary' %}

        {# post have a tease and a markup_style attributes #}
        {% render_content post 'tease' 'markup_style' %}

        {# essay have a content and markup_lang attributes #}
        {% render_content essay 'content' 'markup_lang' %}

    """
    return {
        "content": getattr(article, content_attr),
        "markup": getattr(article, markup_attr),
    }


@register.inclusion_tag("wiki/inlines/alphabet_list.html")
def alphabet_list(articles):
    """Renders a template showing an alphabet list."""
    alphabet = {}
    for article in articles:
        if article.title[0].upper() not in alphabet:
            alphabet.update({article.title[0].upper(): slugify(article.title)})
    return {
        "alphabet": alphabet,
    }
