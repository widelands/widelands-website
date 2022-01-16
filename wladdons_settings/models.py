from django.db import models
from django.contrib.auth.models import User


class AddonNoticeType(models.Model):

    display = models.CharField(
        max_length=50,
        help_text='E.g.: Translation issues'
    )
    description = models.CharField(
        max_length=100,
        help_text='E.g.: Notify me on translation issues'
    )
    send_default = models.BooleanField(
        default=True,
        help_text='Default setting for this notice type'
    )
    slug = models.SlugField(unique=True,
                            help_text='Do not change this once it is set')

    def __str__(self):
        return self.display

    class Meta:
        verbose_name = 'Addon notice type'
        verbose_name_plural = 'Addon notice types'


class AddonNoticeUser(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    notice_type = models.ForeignKey(
        AddonNoticeType,
        on_delete=models.CASCADE
    )
    shouldsend = models.BooleanField(default=True)

    def __str__(self):
        return self.notice_type.display

    class Meta:
        verbose_name = 'Addon noticetype/user relationship'
        verbose_name_plural = 'Addon noticetype/user relationships'


def get_addon_usersetting(user, noticetype):
    """Returns the usersetting for a user.

    If there is no setting yet, create it.
    """

    usersetting, created = AddonNoticeUser.objects.update_or_create(
        user=user,
        notice_type=noticetype
    )

    if created:
        usersetting.shouldsend = noticetype.send_default
        usersetting.save()

    return usersetting
