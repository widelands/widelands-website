from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from widelands.news.models import Post, Category


class NewsPostsFeed(Feed):
    title = 'Widelands news posts feed'
    description = 'The news section from the widelands.org homepage'
    title_template = 'feeds/posts_title.html'
    description_template = 'feeds/posts_description.html'

    def link(self):
        return reverse('news_index')

    def items(self):
        return Post.objects.published()[:10]

    def item_pubdate(self, obj):
        return obj.publish


class NewsPostsByCategory(Feed):
    title = 'Widelands.org posts category feed'

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Category.objects.get(slug__exact=bits[0])

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Posts recently categorized as %s" % obj.title

    def items(self, obj):
        return obj.post_set.published()[:10]
