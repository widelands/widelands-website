from django.contrib.syndication.views import Feed
from django.urls import reverse
from news.models import Post

# Validated through http://validator.w3.org/feed/


class NewsPostsFeed(Feed):
    # RSS Feed
    title = "Widelands news feed"
    description = "The news section from the widelands.org homepage"
    title_template = "news/feeds/posts_title.html"
    description_template = "news/feeds/posts_description.html"

    def items(self):
        return Post.objects.published()[:10]

    def link(self):
        return reverse("news_index")

    def item_pubdate(self, item):
        return item.publish
