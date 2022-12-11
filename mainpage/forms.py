#!/usr/bin/env python -tt
# encoding: utf-8

from django import forms
from django_registration.forms import RegistrationForm
from nocaptcha_recaptcha.fields import NoReCaptchaField
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from wlprofile.models import TZ_CHOICES
from django.shortcuts import get_object_or_404


class RegistrationWithCaptchaForm(RegistrationForm):
    """Overwritten form containing a recaptcha"""

    captcha = NoReCaptchaField()


class ContactForm(forms.Form):
    surname = forms.CharField(max_length=80, required=False)
    forename = forms.CharField(max_length=80, required=False)
    email = forms.EmailField()
    inquiry = forms.CharField(widget=forms.Textarea)
    answer = forms.CharField()
    question = forms.CharField()


class LoginTimezoneForm(AuthenticationForm):
    """Login form with time zone fields."""

    browser_timezone = forms.FloatField(
        label="Time difference to UTC",
        disabled=False,
        widget=forms.HiddenInput,
    )
    set_timezone = forms.BooleanField(
        label="Save this time zone in your profile",
        label_suffix="",
        required=False,
        initial=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        # now the user is logged in
        print(cleaned_data)
        br_time_zone = cleaned_data.get("browser_timezone")
        set_timezone = cleaned_data.get("set_timezone")
        user = get_object_or_404(User, username=cleaned_data.get("username"))
        if set_timezone:
            user_tz = user.wlprofile.time_zone
            if user_tz != br_time_zone:
                for value, display in TZ_CHOICES:
                    if value == br_time_zone:
                        user.wlprofile.time_zone = br_time_zone
                        user.wlprofile.save()
                        break;

        print(user.wlprofile.get_time_zone_display(), user.is_authenticated)
