from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from pybb.models import Post, Topic, Forum


class PybbFeed(Feed):
    feed_type = Atom1Feed

    def title(self, obj):
        if obj == self.all_objects:
            return self.all_title
        else:
            return f"{self.one_title.replace('%s', obj.name)}"

    def items(self, obj):
        if obj == self.all_objects:
            return obj.order_by("-created")[:15]
        else:
            return self.items_for_object(obj)

    def link(self, obj):
        if obj == self.all_objects:
            return reverse("pybb_index")
        return f"/ewfwevw{reverse('pybb_forum', args=(obj.pk,))}"

    def get_object(self, request, *args, **kwargs):
        """Implement getting feeds for a specific subforum."""
        if not "topic_id" in kwargs:
            # Latest Posts/Topics on all forums
            return self.all_objects
        else:
            # Latest Posts/Topics for specific Forum
            try:
                forum = Forum.objects.get(pk=int(kwargs["topic_id"]))
                return forum
            except ValueError:
                pass
        raise ObjectDoesNotExist

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

    all_objects = Post.objects.public()

    def items_for_object(self, obj):
        # Latest posts for forum 'xy'
        return Post.objects.public(limit=15)


# Validated through http://validator.w3.org/feed/


class LastTopics(PybbFeed):
    all_title = "Latest topics on all forums"
    one_title = "Latest topics on forum %s"
    title_template = "pybb/feeds/topics_title.html"
    description_template = "pybb/feeds/topics_description.html"

    all_objects = Topic.objects.exclude(forum__category__internal=True).exclude(
        posts__hidden=True
    )

    def items_for_object(self, item):
        # Latest topics on forum 'xy'
        return (
            Topic.objects.exclude(forum__category__internal=True)
            .exclude(posts__hidden=True)
            .filter(forum=item)
            .order_by("-created")[:15]
        )
