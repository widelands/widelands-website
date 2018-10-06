# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from privacy_policy.models import PrivacyPolicy
from django.core.exceptions import ObjectDoesNotExist


def _format_text(language, text):
    return '[TOC]\n\n#{}\n{}'.format(language, text)
    
    
def privacy_policy(request, *args, **kwargs):
    """Creates the text of a policy and prepare it for markdown."""

    # Defaults to 'English'
    lang = kwargs.pop('lang', 'English')
    policies = PrivacyPolicy.objects.all()

    try:
        policy = policies.get(language=lang)
    except ObjectDoesNotExist:
        # Lets try to find a valid policy
        try:
            policy = policies.all()[0]
        except IndexError:
            policy = None
            text = 'No Policy created yet!'
            languages = ''

    if policy:
        text = _format_text(policy.language, policy.policy_text)
        languages = [x.language for x in policies.exclude(language=lang)]
        
    context = {
        'text': text,
        'languages': languages,
    }
    return render(request, 'privacy_policy.html', context)
