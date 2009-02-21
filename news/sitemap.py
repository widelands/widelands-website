from django.contrib.sitemaps import Sitemap
from widelands.news.models import Post


class NewsSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.published()

        def lastmod(self, obj):
            return obj.publish
