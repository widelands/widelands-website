#!/usr/bin/env python -tt
# encoding: utf-8

from django import forms
from django_registration.forms import RegistrationForm
from nocaptcha_recaptcha.fields import NoReCaptchaField
from wlprofile.models import Profile as wlprofile

# Overwritten form to include a captcha


class RegistrationWithCaptchaForm(RegistrationForm):
    captcha = NoReCaptchaField()


class ContactForm(forms.Form):
    surname = forms.CharField(max_length=80, required=False)
    forename = forms.CharField(max_length=80, required=False)
    email = forms.EmailField()
    inquiry = forms.CharField(widget=forms.Textarea)
    answer = forms.CharField()
    question = forms.CharField()
