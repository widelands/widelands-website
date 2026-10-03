#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Holger Rapp on 2009-03-15.
#
# Last Modified: $Date$
#

from django import forms
from .fields import MAX_IMAGE_PIXELS
from .models import Profile
from mainpage.validators import check_utf8mb3
from django.conf import settings
import re

from django.core.mail import send_mail
from django.template.loader import render_to_string


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    current_password = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    signature = forms.CharField(
        required=False,
        widget=forms.Textarea,
        validators=[
            check_utf8mb3,
        ],
    )

    webservice_nick = forms.CharField(
        required=False,
        validators=[
            check_utf8mb3,
        ],
    )

    class Meta:
        model = Profile
        fields = [
            "avatar",
            "location",
            "email",
            "current_password",
            "operating_system",
            "widelands_version",
            "webservice_nick",
            "favourite_map",
            "favourite_tribe",
            "favourite_addon",
            "signature",
            "show_signatures",
            "time_zone",
            "time_display",
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")

        super(EditProfileForm, self).__init__(instance=instance, *args, **kwargs)

        self.fields["email"].initial = instance.user.email

    def clean_avatar(self):
        avatar = self.cleaned_data["avatar"]
        # 'image' is set by forms.ImageField for new uploads. It is not
        # decoded yet, only the header has been read.
        image = getattr(avatar, "image", None)
        if image is not None and image.width * image.height > MAX_IMAGE_PIXELS:
            raise forms.ValidationError(
                f"The image is too large, it may have at most "
                f"{MAX_IMAGE_PIXELS // 1000000} megapixels"
            )
        return avatar

    def clean_signature(self):
        value = self.cleaned_data["signature"].strip()
        if len(re.findall(r"\n", value)) > settings.SIGNATURE_MAX_LINES:
            raise forms.ValidationError(
                f"Number of lines is limited to {settings.SIGNATURE_MAX_LINES}"
            )
        if len(value) > settings.SIGNATURE_MAX_LENGTH:
            raise forms.ValidationError(
                f"Length of signature is limited to {settings.SIGNATURE_MAX_LENGTH}"
            )
        return value

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        user = self.instance.user
        # Without this check a hijacked session could set a new address and
        # take over the account via a password reset.
        if email and email != user.email:
            if not user.check_password(cleaned_data.get("current_password")):
                self.add_error(
                    "current_password",
                    "Enter your current password to change your email address.",
                )
        return cleaned_data

    def save(self, *args, **kwargs):
        super(EditProfileForm, self).save(*args, **kwargs)

        u = self.instance.user
        old_email = u.email
        u.email = self.cleaned_data["email"]

        u.save(*args, **kwargs)

        if old_email and old_email != u.email:
            send_mail(
                "Your email address on widelands.org was changed",
                render_to_string(
                    "wlprofile/email_changed.txt",
                    {"user": u, "new_email": u.email},
                ),
                settings.DEFAULT_FROM_EMAIL,
                [old_email],
            )
