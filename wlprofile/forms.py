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
    delete_avatar = forms.BooleanField(initial=False,required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['site', 'jabber', 'icq', 'msn', 'aim', 'yahoo',
                  'location', 'signature', 'time_zone', "time_display",
                  'avatar', 'delete_avatar', 'show_signatures', "email",
                  ]


    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")

        super(EditProfileForm, self).__init__(instance=instance, *args,**kwargs)

        self.fields['email'].initial = instance.user.email

    def clean_signature(self):
        value = self.cleaned_data['signature'].strip()
        if len(re.findall(r'\n', value)) > settings.SIGNATURE_MAX_LINES:
            raise forms.ValidationError('Number of lines is limited to %d' % _settings.SIGNATURE_MAX_LINES)
        if len(value) > settings.SIGNATURE_MAX_LENGTH:
            raise forms.ValidationError('Length of signature is limited to %d' % settings.SIGNATURE_MAX_LENGTH)
        return value

    def save(self, *args, **kwargs):
        super(EditProfileForm, self).save(*args, **kwargs)

        u = self.instance.user
        u.email = self.cleaned_data['email']

        u.save(*args, **kwargs)



