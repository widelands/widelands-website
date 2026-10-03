from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from pybb.models import Post, Topic, Forum


class PybbFeed(Feed):
    feed_type = Atom1Feed

    def title(self, obj):
        if obj is None:
            return self.all_title
        return self.one_title % obj.name

    def items(self, obj):
        qs = self.public_items()
        if obj is not None:
            qs = qs.filter(**{self.forum_lookup: obj})
        return qs.order_by("-created")[:15]

    def link(self, obj):
        if obj is None:
            return reverse("pybb_index")
        return reverse("pybb_forum", args=(obj.pk,))

    def get_object(self, request, *args, **kwargs):
        """Return the forum of the feed, or None for the feed of all forums.

        Internal forums have no feed: Forum.DoesNotExist results in a 404.
        """
        if "topic_id" not in kwargs:
            return None
        return Forum.objects.get(pk=kwargs["topic_id"], category__internal=False)

    # Must be used for valid Atom feeds
    def item_updateddate(self, obj):
        return obj.created

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.user


# Validated through http://validator.w3.org/feed/


class LastPosts(PybbFeed):
    all_title = "Latest posts on all forums"
    one_title = "Latest posts on forum %s"
    title_template = "pybb/feeds/posts_title.html"
    description_template = "pybb/feeds/posts_description.html"

    forum_lookup = "topic__forum"

    def public_items(self):
        return Post.objects.public()


# Validated through http://validator.w3.org/feed/


class LastTopics(PybbFeed):
    all_title = "Latest topics on all forums"
    one_title = "Latest topics on forum %s"
    title_template = "pybb/feeds/topics_title.html"
    description_template = "pybb/feeds/topics_description.html"

    forum_lookup = "forum"

    def public_items(self):
        return Topic.objects.exclude(forum__category__internal=True).exclude(
            posts__hidden=True
        )
