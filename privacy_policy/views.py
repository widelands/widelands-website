# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from privacy_policy.models import PrivacyPolicy

def _format_text(language, text):
    return '[TOC]\n\n#{}\n{}'.format(language, text)
    
    
def privacy_policy(request, lang='English'):
    """Creates the text of a policy and prepare them for markdown."""

    try:
        policies = PrivacyPolicy.objects.all()
        policy = policies.get(language=lang)
        text = _format_text(policy.language, policy.policy_text)
        languages = [x.language for x in policies.exclude(language=lang)]
    except:
        text = 'Missing policy'
        languages = ''

    context = {
        'text': text,
        'languages': languages,
    }
    return render(request, 'privacy_policy.html', context)
