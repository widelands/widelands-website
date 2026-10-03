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
from django.utils.translation import gettext_lazy as _

import hashlib
import base64


class GGZAuth(models.Model):
    user = AutoOneToOneField(
        User, related_name="wlggz", verbose_name=_("User"), on_delete=models.CASCADE
    )
    password = models.CharField(
        _("ggz password"), max_length=80, blank=True, default=""
    )
    permissions = models.IntegerField(_("ggz permissions"), default=7)

    class Meta:
        verbose_name = _("ggz")
        verbose_name_plural = _("ggz")

    def set_password(self, raw_password):
        """Store raw_password in the format the metaserver expects."""
        self.password = ggz_password_hash(raw_password)


def ggz_password_hash(raw_password):
    """base64(sha1(password)), as checked by the metaserver and add-on server."""
    pw_hash = hashlib.sha1(raw_password.encode("utf-8")).digest()
    return base64.standard_b64encode(pw_hash).decode("ascii")
