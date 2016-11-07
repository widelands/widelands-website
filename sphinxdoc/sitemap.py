from django.contrib.sitemaps import Sitemap
from sphinxdoc.models import App
import datetime
import os

app = App.objects.get(slug = 'wl')

class DocumentationSitemap(Sitemap):
    """This is just a dummy class to return the link to docs/wl/genindex."""
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return ['']

    def location(self, item):
        return '/docs/wl/genindex/'

    def lastmod(self, item):
        return datetime.datetime.fromtimestamp(
                os.path.getmtime(os.path.join(app.path, 'last_build')))
