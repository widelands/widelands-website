# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from privacy_policy.models import PrivacyPolicy


def _format_text(language, text):
    return '[TOC]\n\n#{}\n{}'.format(language, text)


def privacy_policy(request, *args, **kwargs):
    """Creates the text of a policy and prepare it for markdown.

    We handle here also a link with no slug (/privacy). In this case try
    to load english, else load the first entry in the DB.
    """

    # Default is 'english'
    slug = kwargs.pop('slug', 'english')
    policies = PrivacyPolicy.objects.all()

    if policies.count():
        try:
            policy = policies.get(slug=slug)
        except ObjectDoesNotExist:
            policy = policies.all()[0]
            slug = policy.slug

        text = _format_text(policy.language, policy.policy_text)
        languages = [(x.language, x.slug) for x in policies.exclude(slug=slug)]
        current_lang = policy.language
    else:
        text = 'No Policy created yet!'
        languages = ''
        current_lang = ''

    context = {
        'text': text,
        'languages': languages,
        'cur_lang': current_lang,
    }

    return render(request, 'privacy_policy/privacy_policy.html', context)
