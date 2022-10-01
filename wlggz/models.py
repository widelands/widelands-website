#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Timo Wingender <timo.wingender@gmx.de> on 2010-06-02.
#
# Last Modified: $Date$
#

from django.db import models
from django.contrib.auth.models import User
from mainpage.wl_utils import AutoOneToOneField
from django.utils.translation import ugettext_lazy as _
from pybb.models import Post

import hashlib
import base64


class GGZAuth(models.Model):
    user = AutoOneToOneField(User, related_name="wlggz", verbose_name=_("User"))
    password = models.CharField(
        _("ggz password"), max_length=80, blank=True, default=""
    )
    permissions = models.IntegerField(_("ggz permissions"), default=7)

    class Meta:
        verbose_name = _("ggz")
        verbose_name_plural = _("ggz")

    def save(self, *args, **kwargs):
        # hash the password
        pw_hash = hashlib.sha1(self.password.encode("utf-8")).digest()
        pw_base64 = base64.standard_b64encode(pw_hash)
        self.password = pw_base64
        # Save into the database
        super(GGZAuth, self).save(*args, **kwargs)
