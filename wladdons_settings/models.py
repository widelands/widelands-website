from django.db import models

class NoticeType(models.Model):

    label = models.CharField(_('label'), max_length=40)
    description = models.CharField(_('description'), max_length=100)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Addon notice type'
        verbose_name_plural = 'Addon notice types'


class NoticeSetting(models.Model):
    """Indicates for a given user whether to send notifications from the widelands addon server.

    Notice types for each user are added if he/she enters the notification page.

    """

    user = models.ForeignKey(User, verbose_name=_('user'))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_('notice type'))
    should_send = models.BooleanField(_('send'))

    class Meta:
        verbose_name = 'notice setting'
        verbose_name_plural = 'notice settings'
        unique_together = ('user', 'notice_type')
