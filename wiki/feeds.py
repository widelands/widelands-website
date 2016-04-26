from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, Template
from django.template.loader import get_template
from wiki.models import ChangeSet, Article
from wiki.utils import get_ct
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed

ALL_ARTICLES = Article.objects.all()
ALL_CHANGES = ChangeSet.objects.all()

class RssHistoryFeed(Feed):

    feed_type = Rss201rev2Feed
    title = 'History for all articles'
    description = 'Recent changes in wiki'
    link = '/wiki/feeds/rss'
    title_template = u'feeds/history_title.html'
    description_template = u'feeds/history_description.html'
    
    def items(self):
        return ChangeSet.objects.order_by('-modified')[:30]

    def item_pubdate(self, item):
        """
        Return the item's pubdate. It's this modified date
        """
        return item.modified

    def item_author_name(self, item):
        """
        Takes the object returned by get_object and returns the feeds's
        auhor's name as a Python string
        """
        if item.is_anonymous_change():
            return _("Anonymous")
        return item.editor.username


class AtomHistoryFeed(RssHistoryFeed):

    feed_type = Atom1Feed
    feed_subtitle = 'Recent changes in wiki'
    link = '/wiki/feeds/atom'

    def item_id(self, item):
        return "%s" % item.id

    def item_title(self, item):
        c = Context({'obj' : item})
        return self.title_template.render(c)

    def item_updated(self, item):
        return item.modified

    def item_authors(self, item):
        if item.is_anonymous_change():
            return [{'name' : _('Anonimous')},]
        return [{'name' : item.editor.username},]

    def item_link(self, item):
        return [{'href': item.get_absolute_url()}, ]

    def item_content(self, item):
        c = Context({'obj' : item,})
        return ({'type': 'html'}, self.description_template.render(c))

    def item_author_name(self, item):
        """
        Takes the object returned by get_object and returns the feeds's
        auhor's name as a Python string
        """
        if item.is_anonymous_change():
            return _("Anonymous")
        return item.editor.username


class RssArticleHistoryFeed(Feed):
    feed_type = Rss201rev2Feed
    title_template = u'feeds/history_title.html'
    description_template = u'feeds/history_description.html'
    
    def get_object(self, request, *args, **kwargs):
        return Article.objects.get(title=kwargs['title'])

    def title(self, item):
        return "History for: %s " % item.title

    def link(self, item):
        if not item:
            raise FeedDoesNotExist
        return item.get_absolute_url()

    def description(self, item):
        return "Recent changes in %s" % item.title

    def items(self, item):
        return ChangeSet.objects.filter(article__id__exact=item.id).order_by('-modified')[:30]

    def item_pubdate(self, item):
        """
        Returns the modified date
        """
        return item.modified


class AtomArticleHistoryFeed(RssArticleHistoryFeed):
    feed_type = Atom1Feed

    def get_object(self, request, *args, **kwargs):
        return Article.objects.get(title=kwargs['title'])

    def feed_title(self, item):
        return "History for: %s " % item.title

    def feed_subtitle(self, item):
        return "Recent changes in %s" % item.title

    def feed_id(self):
        return "feed_id"

    def item_id(self, item):
        return "%s" % item.id

    def item_title(self, item):
        c = Context({'obj' : item})
        return self.title_template.render(c)

    def item_updated(self, item):
        return item.modified

    def item_authors(self, item):
        if item.is_anonymous_change():
            return [{'name' : _('Anonimous')},]
        return [{'name' : item.editor.username},]

    def item_links(self, item):
        return [{'href': item.get_absolute_url()},]

    def item_content(self, item):
        c = Context({'obj' : item, })
        return ({'type': 'html'}, self.description_template.render(c))
