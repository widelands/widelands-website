from django.db import models
from django.contrib.auth.models import User
from fields import AutoOneToOneField, ExtendedImageField
from django.utils.translation import ugettext_lazy as _
from pybb.models import Post

import settings

TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
)]

class Profile(models.Model):
    user = AutoOneToOneField(User, related_name='wlprofile', verbose_name=_('User'))

    # Web related fields.
    site = models.URLField(_('Site'), verify_exists=False, blank=True, default='')
    jabber = models.CharField(_('Jabber'), max_length=80, blank=True, default='')
    icq = models.CharField(_('ICQ'), max_length=12, blank=True, default='')
    msn = models.CharField(_('MSN'), max_length=80, blank=True, default='')
    aim = models.CharField(_('AIM'), max_length=80, blank=True, default='')
    yahoo = models.CharField(_('Yahoo'), max_length=80, blank=True, default='')

    # Personal Informations
    location = models.CharField(_('Location'), max_length=30, blank=True, default='')

    # Configuration for Forum/Site
    time_zone = models.FloatField(_('Time zone'), choices=TZ_CHOICES, default=float(settings.DEFAULT_TIME_ZONE))
    time_display = models.CharField(_('Time display'), max_length=80, default=r"%ND(m-d-y), H:i")
    signature = models.TextField(_('Signature'), blank=True, default='', max_length=settings.SIGNATURE_MAX_LENGTH)
    # language = models.CharField(_('Language'), max_length=10, blank=True, default='',
    #                             choices=settings.LANGUAGES)

    avatar = ExtendedImageField(_('Avatar'), blank=True, default='', upload_to=settings.AVATARS_UPLOAD_TO, width=settings.AVATAR_WIDTH, height=settings.AVATAR_HEIGHT)
    show_signatures = models.BooleanField(_('Show signatures'), blank=True, default=True)
    # markup = models.CharField(_('Default markup'), max_length=15, default=settings.DEFAULT_MARKUP, choices=MARKUP_CHOICES)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


    def unread_pm_count(self):
        return PrivateMessage.objects.filter(dst_user=self, read=False).count()

    def post_count(self):
        """
        Return the nr of posts the user has. This uses djangos filter feature
        will therefore hit the database. This should maybe be reworked when the 
        database grows to not be always calculated.
        """
        return Post.objects.filter(user=self.user).count()

