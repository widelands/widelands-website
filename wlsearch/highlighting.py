import re
from html import unescape

from django.utils.html import escape, format_html, strip_tags
from django.utils.safestring import SafeData, mark_safe

from wlsearch.fulltext import SearchQuery


class EscapingHighlighter:
    """Creates a snippet of a text in which the words matching a search query
    are highlighted.

    The text block is treated as plain text and escaped before the matches are
    wrapped in the highlight tag. Text marked as safe (rendered HTML) is
    converted to plain text first.

    Finding the snippet window follows django-haystack's Highlighter.
    """

    css_class = "highlighted"
    html_tag = "span"

    def __init__(self, query, max_length=200):
        words = sorted(SearchQuery(query).highlight_words, key=len, reverse=True)
        # Words beginning with a query word, like the FULLTEXT search finds them
        self.pattern = None
        if words:
            self.pattern = re.compile(
                rf"(?<!\w)(?:{'|'.join(map(re.escape, words))})\w*", re.IGNORECASE
            )
        self.max_length = int(max_length)

    def highlight(self, text_block):
        if isinstance(text_block, SafeData):
            text_block = unescape(strip_tags(text_block))
        self.text_block = str(text_block)
        matches = self.find_matches()
        start_offset, end_offset = self.find_window([start for start, _ in matches])
        return self.render_html(matches, start_offset, end_offset)

    def find_matches(self):
        """Return the start and end offsets of the matching words."""
        if not self.pattern:
            return []
        return [match.span() for match in self.pattern.finditer(self.text_block)]

    def find_window(self, words_found):
        """Return the start and end offset of the window of max_length that
        contains the most matches; the earliest one if several do.
        """
        if not words_found:
            return (0, self.max_length)
        if len(words_found) == 1:
            return (words_found[0], words_found[0] + self.max_length)

        best_start = 0
        best_end = self.max_length
        if words_found[0] > self.max_length:
            best_start = words_found[0]
            best_end = best_start + self.max_length

        highest_density = 0
        for count, start in enumerate(words_found[:-1]):
            current_density = 1
            for end in words_found[count + 1 :]:
                if end - start < self.max_length:
                    current_density += 1
                else:
                    current_density = 0
                if current_density > highest_density:
                    best_start = start
                    best_end = start + self.max_length
                    highest_density = current_density
        return (best_start, best_end)

    def render_html(self, matches, start_offset, end_offset):
        hl_start = format_html('<{} class="{}">', self.html_tag, self.css_class)
        hl_end = format_html("</{}>", self.html_tag)

        parts = ["..."] if start_offset > 0 else []
        copied = start_offset
        for start, end in matches:
            # Skip matches outside of the window
            if start < start_offset:
                continue
            if start >= end_offset:
                break
            end = min(end, end_offset)
            parts += [
                escape(self.text_block[copied:start]),
                hl_start,
                escape(self.text_block[start:end]),
                hl_end,
            ]
            copied = end
        parts.append(escape(self.text_block[copied:end_offset]))
        if end_offset < len(self.text_block):
            parts.append("...")

        return mark_safe("".join(parts))
