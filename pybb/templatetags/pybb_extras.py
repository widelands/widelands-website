# coding=UTF-8

from datetime import datetime, timedelta
import re
from pprint import pprint

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils import dateformat

from pybb.models import Post, Forum, Topic, Read, Category
from pybb.unread import cache_unreads
from pybb import settings as pybb_settings
import pybb.views

register = template.Library()


@register.tag
def pybb_time(parser, token):
    print("Franku in pybb_time: ", parser)
    try:
        tag, time = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'pybb_time requires single argument')
    else:
        return PybbTimeNode(time)


class PybbTimeNode(template.Node):

    def __init__(self, time):
        self.time = template.Variable(time)

    def render(self, context):
        time = self.time.resolve(context)

        delta = datetime.now() - time
        today = datetime.now().replace(hour=0, minute=0, second=0)
        yesterday = today - timedelta(days=1)

        if delta.days == 0:
            if delta.seconds < 60:
                if context['LANGUAGE_CODE'].startswith('ru'):
                    msg = _('seconds ago,seconds ago,seconds ago')
                    import pytils
                    msg = pytils.numeral.choose_plural(delta.seconds, msg)
                else:
                    msg = _('seconds ago')
                return u'%d %s' % (delta.seconds, msg)

            elif delta.seconds < 3600:
                minutes = int(delta.seconds / 60)
                if context['LANGUAGE_CODE'].startswith('ru'):
                    msg = _('minutes ago,minutes ago,minutes ago')
                    import pytils
                    msg = pytils.numeral.choose_plural(minutes, msg)
                else:
                    msg = _('minutes ago')
                return u'%d %s' % (minutes, msg)
        if time > today:
            return _('today, %s') % time.strftime('%H:%M')
        elif time > yesterday:
            return _('yesterday, %s') % time.strftime('%H:%M')
        else:
            return dateformat.format(time, 'd M, Y H:i')


@register.inclusion_tag('pybb/last_posts.html', takes_context=True)
def pybb_last_posts(context, number=8):
    if pybb.views.allowed_for(context.request.user):
        last_posts = Post.objects.filter(
            hidden=False).order_by(
            '-created')[:45]
    else:
        last_posts = Post.objects.filter(
            hidden=False, topic__forum__category__internal=False).order_by(
            '-created')[:45]
            

    check = []
    answer = []
    for post in last_posts:
        if not post.topic.is_hidden:
            if (post.topic_id not in check) and len(check) < number:
                check = check + [post.topic_id]
                answer = answer + [post]
    return {
        'posts': answer,
    }


@register.simple_tag
def pybb_link(object, anchor=u''):
    """Return A tag with link to object."""

    url = hasattr(
        object, 'get_absolute_url') and object.get_absolute_url() or None
    anchor = anchor or smart_unicode(object)
    return mark_safe('<a href="%s">%s</a>' % (url, escape(anchor)))


@register.filter
def pybb_has_unreads(topic, user):
    """Check if topic has messages which user didn't read."""

    now = datetime.now()
    delta = timedelta(seconds=pybb_settings.READ_TIMEOUT)

    def _is_topic_read(topic, user):
        if (now - delta > topic.updated):
            return True
        else:
            if hasattr(topic, '_read'):
                read = topic._read
            else:
                try:
                    read = Read.objects.get(user=user, topic=topic)

                except Read.DoesNotExist:
                    read = None

            if read is None:
                return False
            else:
                return topic.updated <= read.time

    if not user.is_authenticated:
        return False
    else:
        if isinstance(topic, Topic):
            return not _is_topic_read(topic, user)
        if isinstance(topic, Forum):
            forum = topic
            for t in forum.topics.exclude(posts__hidden=True):
                rv = _is_topic_read(t, user)

                if rv == False:
                    return True
            return False
        else:
            raise Exception('Object should be a topic')


@register.filter
def pybb_setting(name):
    return mark_safe(getattr(pybb_settings, name, 'NOT DEFINED'))


@register.filter
def pybb_moderated_by(instance, user):
    """Check if user is superuser or moderator in this forum."""
    try:
        if isinstance(instance, Forum):
            return user.is_superuser or user in instance.moderator_group.user_set.all()
        if isinstance(instance, Topic):
            return user.is_superuser or user in instance.forum.moderator_group.user_set.all()
        if isinstance(instance, Post):
            return user.is_superuser or user in instance.topic.forum.moderator_group.user_set.all()
    except:
        pass
    
    return False
    


@register.filter
def pybb_editable_by(post, user):
    """Check if the post could be edited by the user."""

    if user.is_superuser:
        return True
    if post.user == user:
        return True
    if user in post.topic.forum.moderator_group.user_set.all():
        return True
    return False


@register.filter
def pybb_posted_by(post, user):
    """Check if the post is writed by the user."""

    return post.user == user


@register.filter
def pybb_equal_to(obj1, obj2):
    """Check if objects are equal."""

    return obj1 == obj2


@register.filter
def pybb_unreads(qs, user):
    return cache_unreads(qs, user)


@register.filter
@stringfilter
def pybb_output_bbcode(post):
    """
    post = post.replace('[b]', '<span class="bold">')
    post = post.replace('[i]', '<span class="italic">')
    post = post.relpace('[u]', '<span class="underline">')

    post = post.replace('[/b]', '</span>')
    post = post.replace('[/i]', '</span>')
    post = post.replace('[/u]', '</span>')
    """
    return pprint(post)


@register.inclusion_tag('mainpage/forum_navigation.html', takes_context=True)
def forum_navigation(context):
    """Makes the forum list available to the navigation.

    Ordering:
    1.: value of 'Position' in pybb.Category
    2.: value of 'Position' of pybb.Forum.

    """

    from pybb.models import Forum
    
    forums = Forum.objects.all()
    
    if context.request.user.is_superuser or pybb.views.allowed_for(context.request.user):
        pass
    else:
        # Don't show internal forums
        forums = forums.filter(category__internal=False)

    return {'forums': forums.order_by('category', 'position')}
