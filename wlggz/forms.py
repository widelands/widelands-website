#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Timo Wingender <timo.wingender@gmx.de> on 2010-06-02.
#
# Last Modified: $Date$
#

from django import forms
from .models import GGZAuth
from django.utils.translation import ugettext_lazy as _


class EditGGZForm(forms.ModelForm):
    password = forms.CharField(
        label=_("Online Gaming Password"),
        widget=forms.PasswordInput(render_value=False),
        required=True,
    )
    password2 = forms.CharField(
        label=_("Enter the password again"),
        widget=forms.PasswordInput(render_value=False),
        required=True,
    )

    class Meta:
        model = GGZAuth
        fields = [
            "password",
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")

        super(EditGGZForm, self).__init__(instance=instance, *args, **kwargs)

    def clean(self):
        cleaned_data = super(EditGGZForm, self).clean()
        pw = cleaned_data.get("password")
        pw2 = cleaned_data.get("password2")
        if pw != pw2:
            self.add_error("password2", "The passwords didn't match")
