import re

from django.contrib.auth.models import User
from django.db.models import Q

from notification import models as notification
from pybb import settings as pybb_settings


def notify(request, topic, post):
    if not topic:
        # Inform subscribers of a new topic
        if post.topic.forum.category.internal:
            # Inform only users which have the permission to enter the
            # internal forum and superusers. Those users have to:
            # - enable 'forum_new_topic' in the notification settings, or
            # - subscribe to an existing topic
            subscribers = User.objects.filter(
                Q(groups__permissions__codename=pybb_settings.INTERNAL_PERM)
                | Q(user_permissions__codename=pybb_settings.INTERNAL_PERM)
            ).exclude(username=request.user.username)
            superusers = User.objects.filter(is_superuser=True).exclude(
                username=request.user.username
            )
            # Combine the querysets, excluding double entrys.
            subscribers = subscribers.union(superusers)
        else:
            # Inform normal users
            subscribers = notification.get_observers_for(
                "forum_new_topic", excl_user=request.user
            )

        notification.send(
            subscribers,
            "forum_new_topic",
            {"topic": post.topic, "post": post, "user": post.topic.user},
        )
        # Topics author is subscriber for all new posts in his topic
        post.topic.subscribers.add(request.user)

    else:
        # Handle auto subscriptions to topics
        notice_type = notification.NoticeType.objects.get(
            label="forum_auto_subscribe"
        )
        notice_setting = notification.get_notification_setting(
            post.user, notice_type, "1"
        )
        if notice_setting.send:
            post.topic.subscribers.add(request.user)

        # Send mails about a new post to topic subscribers
        notification.send(
            post.topic.subscribers.exclude(username=post.user),
            "forum_new_post",
            {"post": post, "topic": topic, "user": post.user},
        )
        # Handle mentions with @username
        mention_re = re.compile(r'@(\S+\b)')
        mentioned_users = mention_re.findall(post.body)
        subscribers = []
        for username in mentioned_users:
            try:
                user_obj = User.objects.get(username=username)

                notice_type = notification.NoticeType.objects.get(
                    label="forum_mention"
                )
                if notification.get_notification_setting(
                    user_obj, notice_type, "1").send:
                    subscribers.append(user_obj)

                notification.send(
                    subscribers, "forum_mention",
                    {"post": post, "user": post.user}
                )
            except User.DoesNotExist:
                pass
