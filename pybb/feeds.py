from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed

from pybb.models import Post, Topic, Forum

class PybbFeed(Feed):
    feed_type = Atom1Feed
   
    def title(self,obj):
        if obj == self.all_objects:
            return self.all_title
        else:
            return self.one_title % obj.name

    def description(self,obj):
        if obj == self.all_objects:
            return self.all_description
        else:
            return self.one_description % obj.name
    
    def items(self, obj):
        if obj == self.all_objects:
            return obj.order_by('-created')[:15]
        else: 
            return self.items_for_object(obj)

    def link(self, obj):
        if obj == self.all_objects:
            return reverse('pybb_index')
        return "/ewfwevw%s" % reverse('pybb_forum', args=(obj.pk,))
   
    def get_object(self,bits):
        """
        Implement getting feeds for a specific subforum
        """
        if len(bits) == 0:
            return self.all_objects
        if len(bits) == 1:
            forum =  Forum.objects.get(pk=int(bits[0]))
            return forum
        raise ObjectDoesNotExist
    
    ##########################
    # Individual items below #
    ##########################
    def item_id(self, obj):
        return str(obj.id)

    def item_pubdate(self, obj):
        return obj.created

    def item_links(self, item):
        return [{'href': item.get_absolute_url()}, ]


class LastPosts(PybbFeed):
    all_title = _('Latest posts on all forums')
    all_description = _('Latest posts on all forums')
    one_title = _('Latest topics on forum %s')
    one_description = _('Latest topics on forum %s')
    title_template = 'pybb/feeds/posts_title.html'
    description_template = 'pybb/feeds/posts_description.html'
    
    all_objects = Post.objects 
    
    def items_for_object(self,obj):
        return Post.objects.filter( topic__forum = obj ).order_by('-created')[:15]

    def item_author_name(self, item):
        """
        Takes the object returned by get_object and returns the feeds's
        auhor's name as a Python string
        """
        return item.user.username


class LastTopics(PybbFeed):
    all_title = _('Latest topics on all forums')
    all_description = _('Latest topics on all forums')
    one_title = _('Latest topics on forum %s')
    one_description = _('Latest topics on forum %s')
    title_template = 'pybb/feeds/topics_title.html'
    description_template = 'pybb/feeds/topics_description.html'
    
    all_objects = Topic.objects 
    
    def items_for_object(self,obj):
        return Topic.objects.filter( forum = obj ).order_by('-created')[:15]

    def item_author_name(self, item):
        """
        Takes the object returned by get_object and returns the feeds's
        auhor's name as a Python string
        """
        return item.user.username

