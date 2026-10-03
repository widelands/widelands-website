#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Timo Wingender <timo.wingender@gmx.de> on 2010-06-02.
#
# Last Modified: $Date$
#

from django import forms
from .models import GGZAuth
from django.utils.translation import gettext_lazy as _


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

    def clean(self):
        cleaned_data = super(EditGGZForm, self).clean()
        pw = cleaned_data.get("password")
        pw2 = cleaned_data.get("password2")
        if pw != pw2:
            self.add_error("password2", "The passwords didn't match")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data["password"])
        if commit:
            instance.save()
        return instance
