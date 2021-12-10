from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from wladdons_settings.settings import ADDONNOTICETYPES as AT


class AddonNotice(models.Model):

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    label = models.CharField(max_length=40,
                             unique=True,
                             help_text='Change this in wladdons_settings.settings')
    display = models.CharField(max_length=50,
                               help_text='Change this in wladdons_settings.settings')
    description = models.CharField(max_length=100,
                                   help_text='Change this in wladdons_settings.settings')
    shouldsend = models.BooleanField(default=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Addon notice'
        verbose_name_plural = 'Addon notices'


def get_addon_setting(user, label):
    """Return AddonType for a specific user."""

    defaults = {'display': AT[label]['display'],
                'description': AT[label]['description']}

    setting, created = AddonNotice.objects.update_or_create(user=user,
                                                            label=label,
                                                            defaults=defaults)
    if created:
        print('AddonSetting created: {}'.format(setting))
    return setting
