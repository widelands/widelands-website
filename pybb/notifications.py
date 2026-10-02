import re

from django.contrib.auth.models import User

from notification import models as notification
from pybb import settings as pybb_settings
from pybb.models import Post, Topic
from pybb.util import allowed_for

MENTION_RE = re.compile(r"@([\w.@+\-]+)")


def readers(users, post):
    """Return the users of 'users' who may read 'post' in the forum.

    Hidden posts and posts of hidden topics are only shown to moderators, so
    nobody gets them by mail. Posts of internal forums only go to users who
    may enter internal forums.
    """
    if post.hidden or post.topic.is_hidden:
        return []
    if post.topic.forum.category.internal:
        return [user for user in users if allowed_for(user)]
    return list(users)


def get_mentions(post):
    """Return the users to inform about being mentioned like @username in a post.

    Every user is returned once, the author never, and only the first
    MAX_MENTIONS different names count, so that a post cannot be used to
    mail bomb people.
    """
    if not isinstance(post, Post):
        raise TypeError("First argument has to be an instance of pybb.Post!")

    names = {}
    for line in post.body.splitlines():
        # Didn't find a way to exclude quoted lines with the regex :(
        if not line.startswith(">"):
            names.update(dict.fromkeys(MENTION_RE.findall(line)))
    names.pop(post.user.username, None)
    names = list(names)[: pybb_settings.MAX_MENTIONS]
    if not names:
        return []

    mentioned = User.objects.filter(username__in=names).exclude(pk=post.user_id)
    notice_type = notification.NoticeType.objects.get(label="forum_mention")
    return [
        user
        for user in readers(mentioned, post)
        if notification.get_notification_setting(user, notice_type).send
    ]


def new_topic_subscribers(post):
    """Return the users to inform about the new topic started by 'post'."""
    observers = notification.get_observers_for(
        "forum_new_topic", excl_user=post.topic.user
    )
    return set(readers(observers, post))


def topic_subscribers(post):
    """Return the subscribers of the topic of 'post' to inform about it."""
    return set(readers(post.topic.subscribers.exclude(pk=post.user_id), post))


def inform_mentioned(mentioned, post):
    if not isinstance(post, Post):
        raise TypeError("Second argument has to be an instance of pybb.Post!")

    notification.send(
        mentioned,
        "forum_mention",
        {"post": post, "topic": post.topic, "user": post.user},
    )


def notify(request, topic, post):
    """Send mails for mentions, topic subscribers and users who are auto subscribers.

    - topic subscribers are all users who clicked 'subscribe' to a topic and the topic author
     himself
    - auto subscribers are all who enabled 'auto subscriptions' and wrote a post in a topic
    - mentioned are all whose name is mentioned like @username in a post
    mentioning takes precedence over all. That is if a user is mentioned he will get only one
     email for mentioning and no email for new topic or new post.
    """

    if not isinstance(post, Post):
        raise TypeError("Third argument has to be an instance of pybb.Post!")

    if not topic:
        # Inform subscribers of a new topic
        # Sound's wrong but for new topics there is no topic instance yet.

        mentions = get_mentions(post)

        # Remove mentioned users from subscribers
        new_subscribers = new_topic_subscribers(post) - set(mentions)

        # Send the mails
        inform_mentioned(mentions, post)
        notification.send(
            new_subscribers,
            "forum_new_topic",
            {"topic": post.topic, "post": post, "user": post.topic.user},
        )

        # Topics author is subscriber for all new posts in his topic
        post.topic.subscribers.add(request.user)

    else:

        if not isinstance(topic, Topic):
            raise TypeError("Second argument has to be an instance of pybb.Topic!")

        # Inform users who auto subscribed to topics
        notice_type = notification.NoticeType.objects.get(label="forum_auto_subscribe")
        notice_setting = notification.get_notification_setting(post.user, notice_type)
        if notice_setting.send:
            post.topic.subscribers.add(request.user)

        mentions = get_mentions(post)

        # Remove mentioned users from topic subscribers
        subscribers = topic_subscribers(post) - set(mentions)

        # Finally send the mails
        inform_mentioned(mentions, post)
        # Send mails about a new post to topic subscribers
        notification.send(
            subscribers,
            "forum_new_post",
            {"post": post, "topic": topic, "user": post.user},
        )
