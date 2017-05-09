from django.db.models import signals

from django.utils.translation import ugettext_noop as _

try:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type('maps_new_map',
                                        _('A new Map is available'),
                                        _('a new map is available for download'),1)

    # TODO (Franku): post_syncdb is deprecated since Django 1.7
    # See: https://docs.djangoproject.com/en/1.8/ref/signals/#post-syncdb
    signals.post_syncdb.connect(create_notice_types,
                                sender=notification)
except ImportError:
    print 'Skipping creation of NoticeTypes as notification app not found'
