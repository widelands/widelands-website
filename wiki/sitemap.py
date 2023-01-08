from wiki.models import Article
from mainpage.sitemaps import SitemapHTTPS


class WikiSitemap(SitemapHTTPS):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Article.objects.exclude(deleted=True)

    def lastmod(self, obj):
        return obj.last_update
