from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        return ['mainpage', 'changelog', 'docs']

    def location(self, item):
        return reverse(item)
