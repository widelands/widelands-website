from .models import Post
from datetime import datetime
from datetime import timedelta
from mainpage.sitemaps import SitemapHTTPS


class NewsSitemap(SitemapHTTPS):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        start_date = datetime.today() - timedelta(days=365 * 2)
        return Post.objects.published().filter(publish__gt=start_date)

    def lastmod(self, obj):
        return obj.publish
