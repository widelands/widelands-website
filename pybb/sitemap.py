from django.contrib.sitemaps import Sitemap
from pybb.models import Forum


class ForumSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Forum.objects.all()

    def lastmod(self, obj):
        return obj.updated
