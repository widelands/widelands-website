#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Timo Wingender <timo.wingender@gmx.de> on 2010-06-02.
#
# Last Modified: $Date$
#

from django import forms
from models import GGZAuth
from django.utils.translation import ugettext_lazy as _

import hashlib
import base64
import settings
import re

class EditGGZForm(forms.ModelForm):
    password = forms.CharField(label=_(u'Online Gaming Password'), widget = forms.PasswordInput(render_value = False), required=True)

    class Meta:
        model = GGZAuth
        fields = [ 'password', ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")

        super(EditGGZForm, self).__init__(instance=instance, *args,**kwargs)

    def clean_password(self):
        pw = self.cleaned_data['password']
        pw_hash = hashlib.sha1(pw).digest()
        pw_base64 = base64.standard_b64encode(pw_hash)
        return pw_base64

    def save(self, *args, **kwargs):
        super(EditGGZForm, self).save(*args, **kwargs)
