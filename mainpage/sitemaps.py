from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class SitemapHTTPS(Sitemap):
    protocol = 'https'


class StaticViewSitemap(SitemapHTTPS):
    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        return ['mainpage', 'changelog']

    def location(self, item):
        return reverse(item)
