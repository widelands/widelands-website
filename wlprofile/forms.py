#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Holger Rapp on 2009-03-15.
#
# Last Modified: $Date$
#

from django import forms
from models import Profile

import settings
import re


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['avatar', 'site', 'location', 'jabber', 'icq', 'msn',
                  'aim', 'yahoo', 'signature', 'email', 'show_signatures',
                  'time_zone', 'time_display', ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')

        super(EditProfileForm, self).__init__(
            instance=instance, *args, **kwargs)

        self.fields['email'].initial = instance.user.email

    def clean_signature(self):
        value = self.cleaned_data['signature'].strip()
        if len(re.findall(r'\n', value)) > settings.SIGNATURE_MAX_LINES:
            raise forms.ValidationError(
                'Number of lines is limited to %d' % settings.SIGNATURE_MAX_LINES)
        if len(value) > settings.SIGNATURE_MAX_LENGTH:
            raise forms.ValidationError(
                'Length of signature is limited to %d' % settings.SIGNATURE_MAX_LENGTH)
        return value

    def save(self, *args, **kwargs):
        super(EditProfileForm, self).save(*args, **kwargs)

        u = self.instance.user
        u.email = self.cleaned_data['email']

        u.save(*args, **kwargs)
