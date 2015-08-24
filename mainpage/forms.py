#!/usr/bin/env python -tt
# encoding: utf-8

from registration.forms import RegistrationForm
from wlrecaptcha.forms import RecaptchaForm, \
    RecaptchaFieldPlaceholder, RecaptchaWidget
from django import forms

class RegistrationWithCaptchaForm(RegistrationForm,RecaptchaForm):
    captcha = RecaptchaFieldPlaceholder(widget=RecaptchaWidget(theme="white"),
                                label="Are you human?")

class ContactForm(forms.Form):
    surname = forms.CharField(max_length=80)
    forename = forms.CharField(max_length=80)
    email = forms.EmailField()
    inquiry = forms.CharField(widget=forms.Textarea)
