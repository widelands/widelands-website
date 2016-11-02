from django.contrib.sitemaps import Sitemap
from wiki.models import Article
from news.models import Post
from datetime import datetime
from datetime import timedelta


class WikiSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.last_update


class NewsSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        start_date = datetime.today() - timedelta(days=365 * 2)
        return Post.objects.filter(publish__gt=start_date)
