# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from privacy_policy.models import PrivacyPolicy


def privacy_policy(request):
    """Creates the text of all policies and prepare them for markdown."""

    text = '[TOC]\n'
    policies = PrivacyPolicy.objects.all()
    for policy in policies:
        text = text + '\n#' + policy.language
        text = text + '\n' + policy.policy_text
        text = text + '\n\n---------------------------'
    return render(request, 'privacy_policy.html', {'text': text})
