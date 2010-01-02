#!/usr/bin/env python -tt
# encoding: utf-8

from registration.forms import RegistrationForm
from wlrecaptcha.forms import RecaptchaForm, \
    RecaptchaFieldPlaceholder, RecaptchaWidget

class RegistrationWithCaptchaForm(RegistrationForm,RecaptchaForm):
    captcha = RecaptchaFieldPlaceholder(widget=RecaptchaWidget(theme="white"),
                                label="Are you human?")


