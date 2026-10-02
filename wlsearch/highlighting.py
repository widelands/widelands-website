from html import unescape

from django.utils.html import escape, format_html, strip_tags
from django.utils.safestring import SafeData, mark_safe
from haystack.utils.highlighting import Highlighter


class EscapingHighlighter(Highlighter):
    """Highlighter whose snippets are safe to insert into HTML.

    The output of haystack's {% highlight %} tag is not autoescaped and its
    default Highlighter only runs strip_tags(), which leaves e.g. a '<' without
    a closing '>' untouched. This highlighter treats the text block as plain
    text and escapes it before wrapping the matches in the highlight tag. Text
    marked as safe (rendered HTML) is converted to plain text first.
    """

    def highlight(self, text_block):
        if isinstance(text_block, SafeData):
            text_block = unescape(strip_tags(text_block))
        self.text_block = str(text_block)
        highlight_locations = self.find_highlightable_words()
        start_offset, end_offset = self.find_window(highlight_locations)
        return self.render_html(highlight_locations, start_offset, end_offset)

    def render_html(self, highlight_locations=None, start_offset=None, end_offset=None):
        text = self.text_block[start_offset:end_offset]
        matches = sorted(
            (location - start_offset, term)
            for term, locations in highlight_locations.items()
            for location in locations
        )

        if self.css_class:
            hl_start = format_html('<{} class="{}">', self.html_tag, self.css_class)
        else:
            hl_start = format_html("<{}>", self.html_tag)
        hl_end = format_html("</{}>", self.html_tag)

        parts = ["..."] if start_offset > 0 else []
        copied = 0
        for offset, term in matches:
            # Skip matches outside of the window or overlapping a previous one
            if offset < copied:
                continue
            actual_term = text[offset : offset + len(term)]
            if actual_term.lower() != term:
                continue
            parts += [
                escape(text[copied:offset]),
                hl_start,
                escape(actual_term),
                hl_end,
            ]
            copied = offset + len(term)
        parts.append(escape(text[copied:]))
        if end_offset < len(self.text_block):
            parts.append("...")

        return mark_safe("".join(parts))
