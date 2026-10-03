from django import template

from wlsearch.highlighting import EscapingHighlighter

register = template.Library()


@register.simple_tag
def highlight(text_block, query, max_length=200):
    """Return an escaped snippet of text_block with the words of the search
    query highlighted."""
    return EscapingHighlighter(query, max_length=max_length).highlight(text_block)
