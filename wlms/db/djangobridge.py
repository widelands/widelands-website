#!/usr/bin/env python
# encoding: utf-8

import base64
import hashlib
import os
import sys

# Setup stuff needed for django
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append("..")

from django.contrib.auth.models import User
from wlggz.models import GGZAuth

class DjangoDatabaseBridge(object):
    _GGZPERMS2PERMS = {
          7: "REGISTERED",
        127: "SUPERUSER",
    }

    def check_user(self, user, password):
        try:
            djuser = User.objects.get(username=user)
            perm = GGZAuth.objects.get(user=djuser)
            cor_digest = base64.standard_b64decode(perm.password)
            given_digest = hashlib.sha1(password).digest()
            if cor_digest == given_digest:
                return self._GGZPERMS2PERMS[perm.permissions]
        except (User.DoesNotExist, GGZAuth.DoesNotExist) as e:
            pass
        return False

    def user_exists(self, user):
        try:
            djuser = User.objects.get(username=user)
            return True
        except User.DoesNotExist:
            pass
        return False


