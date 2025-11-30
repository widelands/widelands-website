from django.utils.translation import gettext_noop as _

try:
    from notification import models as notification

    def create_notice_types(sender, **kwargs):
        print("Creating noticetypes for pybb ...")
        notification.create_notice_type(
            "forum_new_topic",
            _("Forum New Topic"),
            _("a new topic has been added to the forum"),
            default=1,
        )
        notification.create_notice_type(
            "forum_new_post",
            _("Forum New Post"),
            _("a new comment has been posted to a topic you observe"),
        )
        notification.create_notice_type(
            "forum_auto_subscribe",
            _("Subscribe automatically"),
            _(
                "once you add a post to an existing topic you will be informed on new posts"
            ),
            default=0,
        )
        notification.create_notice_type(
            "forum_mention",
            _("Your name was mentioned"),
            _("someone has mentioned your name with '@name' in a post"),
            # enabled by default
            default=2,
        )

except ImportError:
    print("Skipping creation of NoticeTypes as notification app not found")
