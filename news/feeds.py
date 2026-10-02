from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from news.models import Post


class NewsPostsFeed(Feed):
    # Validated through http://validator.w3.org/feed/ on 2026-01-28
    feed_type = Atom1Feed
    title = "Widelands news feed"
    subtitle = "The news section from the widelands.org homepage"
    title_template = "news/feeds/posts_title.html"
    description_template = "news/feeds/posts_description.html"

    def items(self):
        return Post.objects.published()[:10]

    def link(self):
        return reverse("news_feed")

    def item_pubdate(self, item):
        return item.publish

    def item_author_name(self, item):
        return item.author

    def item_updateddate(self, item):
        return item.modified
