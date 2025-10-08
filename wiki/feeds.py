from django.contrib.syndication.views import Feed, FeedDoesNotExist
from wiki.models import ChangeSet, Article
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed

# Validated through http://validator.w3.org/feed/


class RssHistoryFeed(Feed):
    feed_type = Rss201rev2Feed
    title = "History for all articles"
    description = "Recent changes in wiki"
    link = "/wiki/feeds/rss/"
    title_template = "wiki/feeds/history_title.html"
    description_template = "wiki/feeds/history_description.html"

    def items(self):
        return ChangeSet.official.order_by("-modified")[:30]

    def item_pubdate(self, item):
        """Return the item's pubdate.

        It's this modified date

        """
        return item.modified


# Validated through http://validator.w3.org/feed/


class AtomHistoryFeed(RssHistoryFeed):
    feed_type = Atom1Feed
    subtitle = "Recent changes in wiki"
    link = "/wiki/feeds/atom/"

    def item_updateddate(self, item):
        return item.modified


# Validated through http://validator.w3.org/feed/


class RssArticleHistoryFeed(Feed):
    feed_type = Rss201rev2Feed
    title_template = "wiki/feeds/history_title.html"
    description_template = "wiki/feeds/history_description.html"

    def get_object(self, request, *args, **kwargs):
        return Article.objects.get(title=kwargs["title"])

    def title(self, item):
        return "History for: %s " % item.title

    def link(self, item):
        if not item:
            raise FeedDoesNotExist
        return item.get_absolute_url()

    def description(self, item):
        return "Recent changes in %s" % item.title

    def items(self, item):
        return (
            ChangeSet.objects.exclude(article__deleted=True)
            .filter(article__id__exact=item.id)
            .order_by("-modified")[:30]
        )

    def item_pubdate(self, item):
        """Returns the modified date."""
        return item.modified


# Validated through http://validator.w3.org/feed/


class AtomArticleHistoryFeed(RssArticleHistoryFeed):
    feed_type = Atom1Feed

    def subtitle(self, item):
        return "Recent changes in %s" % item.title

    def item_updateddate(self, item):
        return item.modified
