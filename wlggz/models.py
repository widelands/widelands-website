
#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Timo Wingender <timo.wingender@gmx.de> on 2010-06-02.
#
# Last Modified: $Date$
#

from django.db import models
from django.contrib.auth.models import User
from wl_utils import AutoOneToOneField
from django.utils.translation import ugettext_lazy as _
from pybb.models import Post

import settings


class GGZAuth(models.Model):
    user = AutoOneToOneField(
        User, related_name='wlggz', verbose_name=_('User'))
    password = models.CharField(
        _('ggz password'), max_length=80, blank=True, default='')
    permissions = models.IntegerField(_('ggz permissions'), default=7)

    class Meta:
        verbose_name = _('ggz')
        verbose_name_plural = _('ggz')
