from django.contrib.syndication.views import Feed, FeedDoesNotExist
from wiki.models import ChangeSet, Article
from django.utils.feedgenerator import Atom1Feed


class WikiHistoryFeed(Feed):
    # Validated through http://validator.w3.org/feed/ on 2026-01-28
    feed_type = Atom1Feed
    title = "History for all articles"
    subtitle = "Recent changes in wiki"
    link = "/feeds/wiki/"
    title_template = "wiki/feeds/history_title.html"
    description_template = "wiki/feeds/history_description.html"

    def items(self):
        return ChangeSet.official.order_by("-modified")[:30]

    def item_author_name(self, item):
        return item.editor

    def item_updateddate(self, item):
        return item.last_update

    def item_updateddate(self, item):
        return item.modified


class WikiArticleHistoryFeed(Feed):
    # Validated through http://validator.w3.org/feed/ on 2026-01-28
    feed_type = Atom1Feed
    title_template = "wiki/feeds/history_title.html"
    description_template = "wiki/feeds/history_description.html"

    def items(self, item):
        return (
            ChangeSet.objects.exclude(article__deleted=True)
            .filter(article__id__exact=item.id)
            .order_by("-modified")[:30]
        )

    def link(self, item):
        if not item:
            raise FeedDoesNotExist
        return item.get_absolute_url()

    def get_object(self, request, *args, **kwargs):
        return Article.objects.get(title=kwargs["title"])

    def title(self, item):
        return "History for: %s " % item.title

    def subtitle(self, item):
        return "Recent changes in %s" % item.title

    def item_author_name(self, item):
        return item.editor

    def item_pubdate(self, item):
        """Returns the modified date."""
        return item.modified

    def item_updateddate(self, item):
        return item.modified
