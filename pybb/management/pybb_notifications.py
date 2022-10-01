from django.utils.translation import ugettext_noop as _

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


except ImportError:
    print("Skipping creation of NoticeTypes as notification app not found")
