#!/usr/bin/env python -tt
# encoding: utf-8

from django import forms
from django_registration.forms import RegistrationForm
from nocaptcha_recaptcha.fields import NoReCaptchaField
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from wlprofile.models import TZ_CHOICES
from django.shortcuts import get_object_or_404
from django.core.mail import mail_admins


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
        required=False,
        widget=forms.HiddenInput,
    )
    set_timezone = forms.BooleanField(
        label="Save this time zone in your profile.",
        label_suffix="",
        required=False,
        initial=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        # now the user is logged in
        br_time_zone = cleaned_data.get("browser_timezone", None)
        set_timezone = cleaned_data.get("set_timezone")
        profile = get_object_or_404(
            User, username=cleaned_data.get("username")
        ).wlprofile
        if (
            set_timezone
            and br_time_zone is not None
            and profile.time_zone != br_time_zone
        ):
            found = False
            for value, display in TZ_CHOICES:
                if value == br_time_zone:
                    profile.time_zone = br_time_zone
                    profile.save()
                    found = True
            if found is False:
                mail_admins(
                    "Missing Time Zone?",
                    "Automatic applying a time zone for user '{user}' has failed. Please check if '{tz}' is a valid time zone and add it to TZ_CHOICES in wlprofile.models".format(
                        user=profile.user.username, tz=br_time_zone
                    ),
                )
                self.add_error(
                    "set_timezone",
                    "The time zone can't be found in our list of time zones. Please disable the checkbox and try again. After successful login please check your time zone in the 'Edit Profile' page. Admins got already informed about this.",
                )
