from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("forum_new_topic",
                                        _("Forum New Topic"),
                                        _("a new topic has been added to the forum"),
                                        default=1)
        notification.create_notice_type("forum_new_post",
                                        _("Forum New Post"),
                                        _("a new comment has been posted to a topic you observe"))

    signals.post_syncdb.connect(create_notice_types,
                                sender=notification)
except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"
