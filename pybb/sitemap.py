from pybb.models import Forum
from mainpage.sitemaps import SitemapHTTPS


class ForumSitemap(SitemapHTTPS):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Forum.objects.all()

    def lastmod(self, obj):
        return obj.updated
