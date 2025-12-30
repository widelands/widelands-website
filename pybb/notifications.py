import re

from django.contrib.auth.models import User
from django.db.models import Q

from notification import models as notification
from pybb import settings as pybb_settings
from pybb.models import Post, Topic

MENTION_RE = re.compile(r"@([\w.@+\-]+)")


def get_mentions(post):
    """Return usernames which are mentioned in a post like @username."""
    if not isinstance(post, Post):
        raise TypeError(f"First argument has to be an instance of pybb.Post!")

    mentioned_names = []
    for line in post.body.splitlines():
        # Didn't find a way to exclude quoted lines with the regex :(
        if not line.startswith(">"):
            mentioned = MENTION_RE.findall(line)
            mentioned_names.extend(mentioned)

    mentioned_users = []
    for username in mentioned_names:
        # Make sure this is an existing user
        try:
            user_obj = User.objects.get(username=username)

            notice_type = notification.NoticeType.objects.get(label="forum_mention")

            if notification.get_notification_setting(user_obj, notice_type).send:
                mentioned_users.append(user_obj)

        except User.DoesNotExist:
            pass

    return mentioned_users


def inform_mentioned(mentioned, post):
    if not isinstance(post, Post):
        raise TypeError(f"Second argument has to be an instance of pybb.Post!")

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
        raise TypeError(f"Third argument has to be an instance of pybb.Post!")

    if not topic:
        # Inform subscribers of a new topic
        # Sound's wrong but for new topics there is no topic instance yet.

        if post.topic.forum.category.internal:
            # Inform only users which have the permission to enter the
            # internal forum and superusers. Those users have to:
            # - enable 'forum_new_topic' in the notification settings, or
            # - subscribed to an existing topic
            subscribers = User.objects.filter(
                Q(groups__permissions__codename=pybb_settings.INTERNAL_PERM)
                | Q(user_permissions__codename=pybb_settings.INTERNAL_PERM)
            ).exclude(username=request.user.username)
            superusers = User.objects.filter(is_superuser=True).exclude(
                username=request.user.username
            )
            # Combine the query sets, excluding double entries.
            subscribers = subscribers.union(superusers)
        else:
            # Normal users
            subscribers = notification.get_observers_for(
                "forum_new_topic", excl_user=request.user
            )

        mentions = get_mentions(post)

        # Remove mentioned users from subscribers
        new_subscribers = set(subscribers) - set(mentions)

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
            raise TypeError(f"Second argument has to be an instance of pybb.Topic!")

        # Inform users who auto subscribed to topics
        notice_type = notification.NoticeType.objects.get(label="forum_auto_subscribe")
        notice_setting = notification.get_notification_setting(
            post.user, notice_type
        )
        if notice_setting.send:
            post.topic.subscribers.add(request.user)

        mentions = get_mentions(post)

        # Remove mentioned users from topic subscribers
        topic_subscribers = set(
            post.topic.subscribers.exclude(username=post.user)
        ) - set(mentions)

        # Finally send the mails
        inform_mentioned(mentions, post)
        # Send mails about a new post to topic subscribers
        notification.send(
            topic_subscribers,
            "forum_new_post",
            {"post": post, "topic": topic, "user": post.user},
        )
