from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['mainpage', 'changelog']

    def location(self, item):
        return reverse(item)
