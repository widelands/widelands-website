from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from news.models import Post, Category

# Validated through http://validator.w3.org/feed/


class NewsPostsFeed(Feed):
    # RSS Feed
    title = 'Widelands news feed'
    description = 'The news section from the widelands.org homepage'
    title_template = 'news/feeds/posts_title.html'
    description_template = 'news/feeds/posts_description.html'

    def items(self):
        return Post.objects.published()[:10]

    def link(self):
        return reverse('news_index')

    def item_pubdate(self, item):
        return item.publish

# Currently not used / not checked for compatibility for django 1.8


class NewsPostsByCategory(Feed):
    title = 'Widelands.org posts category feed'

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Category.objects.get(slug__exact=bits[0])

    def link(self, item):
        if not item:
            raise FeedDoesNotExist
        return item.get_absolute_url()

    def description(self, item):
        return 'Posts recently categorized as %s' % item.title

    def items(self, item):
        return item.post_set.published()[:10]
