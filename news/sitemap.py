from django.contrib.sitemaps import Sitemap
from .models import Post
from datetime import datetime
from datetime import timedelta


class NewsSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        start_date = datetime.today() - timedelta(days=365 * 2)
        return Post.objects.published().filter(publish__gt=start_date)

    def lastmod(self, obj):
        return obj.publish
