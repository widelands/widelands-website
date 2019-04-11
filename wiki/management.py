
from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification

    def create_notice_types(sender, **kwargs):
        print("Creating noticetypes for wiki ...")
        notification.create_notice_type('wiki_revision_reverted',
                                        _('Article Revision Reverted'),
                                        _('your revision has been reverted'))
        notification.create_notice_type('wiki_observed_article_changed',
                                        _('Observed Article Changed'),
                                        _('an article you observe has changed'))

except ImportError:
    print('Skipping creation of NoticeTypes as notification app not found')
