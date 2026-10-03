#!/usr/bin/env python -tt
# encoding: utf-8

import logging

from django import forms
from django_registration.forms import RegistrationForm
from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.forms import AuthenticationForm
from wlprofile.models import TZ_CHOICES

logger = logging.getLogger(__name__)


class FormWithCaptcha(RegistrationForm):
    """Overwritten form containing a recaptcha"""

    captcha = ReCaptchaField()


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
        # Only touch the profile of a successfully authenticated user. The
        # parent's clean() skips authentication if a field (e.g. the password)
        # is missing, so do not rely on it having raised.
        user = self.get_user()
        if user is None:
            return cleaned_data
        br_time_zone = cleaned_data.get("browser_timezone", None)
        set_timezone = cleaned_data.get("set_timezone")
        profile = user.wlprofile
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
                logger.warning(
                    "Unknown browser time zone offset %r on login of user %r",
                    br_time_zone,
                    profile.user.username,
                )
                self.add_error(
                    "set_timezone",
                    "The time zone can't be found in our list of time zones. Please disable the checkbox and try again. After successful login please check your time zone in the 'Edit Profile' page.",
                )
        return cleaned_data
