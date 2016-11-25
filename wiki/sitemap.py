from django.contrib.sitemaps import Sitemap
from wiki.models import Article


class WikiSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.last_update
