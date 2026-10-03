from django.test import SimpleTestCase

from pybb.util import urlize


class TestUrlize(SimpleTestCase):
    def test_escaped_script_block_stays_escaped(self):
        html = "<p>Before</p>\n&lt;script&gt;alert(1)&lt;/script&gt;\n<p>After</p>"
        self.assertEqual(urlize(html), html)

    def test_plain_url_becomes_link(self):
        self.assertEqual(
            urlize("<p>a &lt; b see https://example.org/x?a=1&amp;b=2</p>"),
            '<p>a &lt; b see <a href="https://example.org/x?a=1&amp;b=2" '
            'rel="nofollow ugc">https://example.org/x?a=1&amp;b=2</a></p>',
        )
