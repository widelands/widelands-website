# coding=UTF-8

from datetime import datetime, timedelta
import re
from pprint import pprint

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.encoding import smart_str
from django.utils.html import escape

from pybb.models import Post, Forum, Topic, Read
from pybb.unread import cache_unreads
from pybb import settings as pybb_settings
from pybb.util import allowed_for

register = template.Library()


@register.inclusion_tag("pybb/last_posts.html", takes_context=True)
def pybb_last_posts(context, number=8):
    BASE_COUNT = 100

    # Create permission dependent Querysets
    if allowed_for(context.request.user):
        last_posts = Post.objects.filter(hidden=False).order_by("-created")[:BASE_COUNT]
    else:
        last_posts = Post.objects.public(limit=BASE_COUNT)

    check = []
    answer = []
    for post in last_posts:
        if (post.topic_id not in check) and len(check) < number:
            check = check + [post.topic_id]
            answer = answer + [post]
    return {
        "posts": answer,
    }


@register.simple_tag
def pybb_link(object, anchor=""):
    """Return A tag with link to object."""

    url = hasattr(object, "get_absolute_url") and object.get_absolute_url() or None
    anchor = anchor or smart_str(object)
    return mark_safe('<a href="%s">%s</a>' % (url, escape(anchor)))


@register.filter
def pybb_has_unreads(topic, user):
    """Check if topic has messages which user didn't read."""

    now = datetime.now()
    delta = timedelta(seconds=pybb_settings.READ_TIMEOUT)

    def _is_topic_read(topic, user):
        if now - delta > topic.updated:
            return True
        else:
            if hasattr(topic, "_read"):
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
            raise Exception("Object should be a topic")


@register.filter
def pybb_setting(name):
    return mark_safe(getattr(pybb_settings, name, "NOT DEFINED"))


@register.filter
def pybb_moderated_by(instance, user):
    """Check if user is superuser or moderator in this forum."""
    try:
        if isinstance(instance, Forum):
            return user.is_superuser or user in instance.moderator_group.user_set.all()
        if isinstance(instance, Topic):
            return (
                user.is_superuser
                or user in instance.forum.moderator_group.user_set.all()
            )
        if isinstance(instance, Post):
            return (
                user.is_superuser
                or user in instance.topic.forum.moderator_group.user_set.all()
            )
    except:
        pass

    return False


@register.filter
def pybb_editable_by(post, user):
    """Check if a user is allowed to edit this post."""

    if not user.is_authenticated:
        # No need to run the other checks
        return False

    if user.is_superuser:
        return True
    try:
        if user in post.topic.forum.moderator_group.user_set.all():
            # Forum moderators are always allowed
            return True
    except AttributeError:
        # Probably there is no moderator_group yet
        pass

    if post.user == user:
        # Restrict the time a user can edit his own post
        edit_time = timedelta(hours=pybb_settings.EDIT_HOURS)
        return datetime.now() <= post.created + edit_time

    return False


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


@register.inclusion_tag("mainpage/forum_navigation.html", takes_context=True)
def forum_navigation(context):
    """Makes the forum list available to the navigation.

    Ordering:
    1.: value of 'Position' in pybb.Category
    2.: value of 'Position' of pybb.Forum.

    """

    forums = Forum.objects.all()

    if allowed_for(context.request.user):
        pass
    else:
        # Don't show internal forums
        forums = forums.filter(category__internal=False)

    return {"forums": forums.order_by("category", "position")}
