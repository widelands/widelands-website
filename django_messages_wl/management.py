#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


if 'notification' in settings.INSTALLED_APPS and getattr(settings, 'DJANGO_MESSAGES_NOTIFY', True):
    from notification import models as notification

    def create_notice_types(sender, **kwargs):
        print('Creating wl specific noticetypes for django-messages ...')
        notification.create_notice_type('messages_received', _(
            'Message Received'), _('you have received a message'), default=2)
        notification.create_notice_type('messages_reply_received', _(
            'Reply Received'), _('you have received a reply to a message'), default=2)
else:
    print('Skipping creation of NoticeTypes as notification app not found')
